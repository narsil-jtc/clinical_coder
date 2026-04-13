"""
Review panel component (right column).

Shows review progress, coding alerts, accepted codes, and export actions.
"""

import csv
import io
from datetime import datetime

import streamlit as st

from ..state_manager import (
    acknowledge_flag,
    all_flags_acknowledged,
    get_acknowledged_flags,
    get_review_decisions,
    get_review_summary,
)
from .confidence_badge import confidence_badge_html


def _build_export_csv(validated_codes: list[dict], decisions: dict) -> str:
    """Build CSV string of accepted and changed codes for export."""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["code", "description", "code_system", "confidence", "decision", "evidence_span"])
    for code_dict in validated_codes:
        code = code_dict.get("code", "")
        dec_data = decisions.get(code, {})
        decision = dec_data.get("decision", "pending")
        if decision in ("accepted", "modified"):
            final_code = dec_data.get("modified_code") or code
            writer.writerow(
                [
                    final_code,
                    code_dict.get("description", ""),
                    code_dict.get("code_system", "ICD-10"),
                    f"{code_dict.get('confidence', 0):.2f}",
                    decision,
                    code_dict.get("evidence_span", ""),
                ]
            )
    return output.getvalue()


def _build_export_text(validated_codes: list[dict], decisions: dict) -> str:
    """Build plain text code list suitable for copy-pasting into an EHR."""

    lines = [f"Clinical Coding Output - {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    lines.append("=" * 50)
    for code_dict in validated_codes:
        code = code_dict.get("code", "")
        dec_data = decisions.get(code, {})
        decision = dec_data.get("decision", "pending")
        if decision in ("accepted", "modified"):
            final_code = dec_data.get("modified_code") or code
            desc = code_dict.get("description", "")
            lines.append(f"{final_code}  {desc}")
    return "\n".join(lines)


def _accepted_codes(validated_codes: list[dict], decisions: dict[str, dict]) -> list[dict]:
    accepted: list[dict] = []
    for code_dict in validated_codes:
        code = code_dict.get("code", "")
        dec_data = decisions.get(code, {})
        decision = dec_data.get("decision", "pending")
        if decision not in ("accepted", "modified"):
            continue
        accepted.append(
            {
                "final_code": dec_data.get("modified_code") or code,
                "description": code_dict.get("description", ""),
                "confidence": code_dict.get("confidence", 0.0),
            }
        )
    return accepted


def _render_accepted_code_row(item: dict) -> None:
    badge = confidence_badge_html(item.get("confidence", 0.0))
    st.markdown(
        (
            '<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;'
            'padding:8px 0;border-bottom:1px solid #f1f5f9;">'
            '<div style="display:flex;align-items:flex-start;gap:8px;">'
            '<span style="color:#15803d;font-weight:700;">&#10003;</span>'
            '<div>'
            f'<div><strong>{item.get("final_code", "")}</strong> &mdash; {item.get("description", "")}</div>'
            "</div>"
            "</div>"
            f"<div>{badge}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_review_panel(
    validated_codes: list[dict],
    all_flags: list[dict],
    workflow_errors: list[str],
    missing_specificity: list[dict],
) -> None:
    """Render the right-hand review status panel."""

    summary = get_review_summary()
    decisions = get_review_decisions()

    st.subheader("Your Review Progress")
    st.markdown(
        '<div style="background:#f0fdf4;border:1px solid #86efac;'
        'border-radius:8px;padding:10px 12px;margin-bottom:10px;">',
        unsafe_allow_html=True,
    )
    col_a, col_r = st.columns(2)
    with col_a:
        st.metric("Accepted", summary.get("accepted", 0))
    with col_r:
        st.metric("Rejected", summary.get("rejected", 0))

    col_m, col_p = st.columns(2)
    with col_m:
        st.metric("Changed", summary.get("modified", 0))
    with col_p:
        st.metric("Not yet reviewed", summary.get("pending", 0))
    st.markdown("</div>", unsafe_allow_html=True)

    accepted_codes = _accepted_codes(validated_codes, decisions)
    with st.expander(
        f"Accepted codes ({len(accepted_codes)})",
        expanded=bool(accepted_codes),
    ):
        if accepted_codes:
            for item in accepted_codes:
                _render_accepted_code_row(item)
        else:
            st.caption("Accepted or changed codes will appear here.")

    st.divider()

    if all_flags:
        acknowledged = get_acknowledged_flags()
        unacked = [flag for flag in all_flags if flag.get("rule_id") not in acknowledged]

        st.subheader(f"Coding alerts ({len(all_flags)})")
        if unacked:
            st.warning(f"{len(unacked)} coding alert(s) still need to be marked as noted before export.")

        severity_styles = {
            "critical": ("&#128308;", "#7f1d1d", "#fee2e2", "#fca5a5"),
            "warning": ("&#128993;", "#713f12", "#fef9c3", "#fde047"),
            "info": ("&#128309;", "#1e3a5f", "#dbeafe", "#93c5fd"),
        }

        for flag in all_flags:
            rule_id = flag.get("rule_id", "")
            is_acked = rule_id in acknowledged
            severity = flag.get("severity", "info")
            icon, text_col, bg, border = severity_styles.get(
                severity,
                ("&#9898;", "#374151", "#f3f4f6", "#d1d5db"),
            )
            opacity = "opacity:0.55;" if is_acked else ""

            with st.container():
                col_flag, col_ack = st.columns([4, 1])
                with col_flag:
                    st.markdown(
                        f'<div style="background:{bg};border-left:3px solid {border};'
                        f'border-radius:0 6px 6px 0;padding:7px 10px;font-size:0.78rem;{opacity}">'
                        f'<div style="font-weight:700;color:{text_col};">{icon} Coding alert</div>'
                        f'<div style="color:{text_col};margin-top:2px;">{flag.get("message", "")}</div>'
                        f'<div style="color:#6b7280;font-style:italic;margin-top:2px;font-size:0.73rem;">'
                        f'{flag.get("suggested_action", "")}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col_ack:
                    if is_acked:
                        st.markdown(
                            '<div style="text-align:center;padding-top:8px;">Noted</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        if st.button("Noted", key=f"ack_{rule_id}_{flag.get('code', '')}"):
                            acknowledge_flag(rule_id)
                            st.rerun()

        st.divider()

    if missing_specificity:
        with st.expander(f"Could be more specific ({len(missing_specificity)})", expanded=False):
            for gap in missing_specificity:
                st.markdown(
                    f"**{gap.get('entity', '')}** - "
                    f"{gap.get('available_specificity', '')} "
                    f"(for example `{gap.get('example_code', '')}`)"
                )

    st.subheader("Export")

    if summary.get("pending", 0):
        st.warning(f"{summary.get('pending', 0)} code(s) still need your review.")

    can_export = all_flags_acknowledged()
    if not can_export:
        st.caption("Mark all coding alerts as noted to enable export.")

    if st.button("Export as CSV", disabled=not can_export, use_container_width=True):
        csv_data = _build_export_csv(validated_codes, decisions)
        st.download_button(
            "Download codes.csv",
            data=csv_data,
            file_name=f"codes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    if st.button("Copy as text", disabled=not can_export, use_container_width=True):
        text = _build_export_text(validated_codes, decisions)
        st.code(text, language=None)

    if workflow_errors:
        with st.expander(f"System notices ({len(workflow_errors)})", expanded=False):
            for err in workflow_errors:
                st.caption(f"Notice: {err}")

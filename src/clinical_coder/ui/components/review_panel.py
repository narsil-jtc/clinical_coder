"""Review panel component (right column)."""

import csv
import io
from datetime import datetime

import streamlit as st

from clinical_coder.ui.theme import status_banner

from ..state_manager import (
    acknowledge_flag,
    all_flags_acknowledged,
    get_acknowledged_flags,
    get_review_decisions,
    get_review_summary,
)
from .confidence_badge import confidence_badge_html


def _build_export_csv(validated_codes: list[dict], decisions: dict) -> str:
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
            '<div style="display:flex;align-items:center;justify-content:space-between;gap:0.7rem;'
            'padding:0.7rem 0;border-bottom:1px solid rgba(16,35,48,0.08);">'
            '<div>'
            f'<div style="font-size:0.9rem;font-weight:700;color:#102330;">{item.get("final_code", "")}</div>'
            f'<div style="font-size:0.82rem;color:#5e7280;margin-top:0.12rem;">{item.get("description", "")}</div>'
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
    diagnostics: dict | None = None,
) -> None:
    summary = get_review_summary()
    decisions = get_review_decisions()

    st.markdown(
        """
<div class="cc-shell">
    <div class="cc-section-kicker">Decision overview</div>
    <h3 class="cc-section-title">Review progress</h3>
    <div class="cc-section-copy">Accepted, rejected, changed, and pending decisions update live as you review.</div>
</div>
        """,
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
        st.metric("Pending", summary.get("pending", 0))

    accepted_codes = _accepted_codes(validated_codes, decisions)
    with st.expander(f"Accepted codes ({len(accepted_codes)})", expanded=bool(accepted_codes)):
        if accepted_codes:
            for item in accepted_codes:
                _render_accepted_code_row(item)
        else:
            st.caption("Accepted or changed codes will appear here.")

    if all_flags:
        acknowledged = get_acknowledged_flags()
        unacked = [flag for flag in all_flags if flag.get("rule_id") not in acknowledged]
        if unacked:
            status_banner(
                f"{len(unacked)} coding alert(s) still need to be marked as noted before export.",
                tone="warning",
            )

        st.markdown(
            """
<div class="cc-shell cc-shell-soft">
    <div class="cc-section-kicker">Attention needed</div>
    <h3 class="cc-section-title">Coding alerts</h3>
</div>
            """,
            unsafe_allow_html=True,
        )

        severity_styles = {
            "critical": ("#9d3e39", "#fde9e6", "#efbbb3"),
            "warning": ("#8b5a16", "#fff3dd", "#f0cf8a"),
            "info": ("#305f84", "#eaf3fb", "#c9ddeb"),
        }

        for flag in all_flags:
            rule_id = flag.get("rule_id", "")
            is_acked = rule_id in acknowledged
            severity = flag.get("severity", "info")
            text_col, bg, border = severity_styles.get(severity, ("#4b5c67", "#f5f7f8", "#d9e1e5"))
            opacity = "0.62" if is_acked else "1"

            col_flag, col_ack = st.columns([4, 1])
            with col_flag:
                st.markdown(
                    (
                        f'<div style="background:{bg};border:1px solid {border};border-radius:16px;'
                        f'padding:0.8rem 0.9rem;opacity:{opacity};">'
                        f'<div style="font-size:0.73rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{text_col};">Coding alert</div>'
                        f'<div style="font-size:0.85rem;color:{text_col};margin-top:0.22rem;line-height:1.48;">{flag.get("message", "")}</div>'
                        f'<div style="font-size:0.77rem;color:#5e7280;margin-top:0.26rem;line-height:1.45;">{flag.get("suggested_action", "")}</div>'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
            with col_ack:
                if is_acked:
                    st.caption("Noted")
                else:
                    if st.button("Noted", key=f"ack_{rule_id}_{flag.get('code', '')}", use_container_width=True):
                        acknowledge_flag(rule_id)
                        st.rerun()

    if missing_specificity:
        with st.expander(f"Could be more specific ({len(missing_specificity)})", expanded=False):
            for gap in missing_specificity:
                st.markdown(
                    f"**{gap.get('entity', '')}** - "
                    f"{gap.get('available_specificity', '')} "
                    f"(for example `{gap.get('example_code', '')}`)"
                )

    st.markdown(
        """
<div class="cc-shell cc-shell-soft">
    <div class="cc-section-kicker">Output</div>
    <h3 class="cc-section-title">Export</h3>
    <div class="cc-section-copy">Only reviewed codes should leave this workspace.</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    if summary.get("pending", 0):
        status_banner(f"{summary.get('pending', 0)} code(s) still need your review.", tone="warning")

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

    if diagnostics:
        counts = diagnostics.get("counts", {})
        trace = diagnostics.get("trace", [])
        with st.expander("Run diagnostics", expanded=bool(workflow_errors) or not validated_codes):
            if counts:
                col_1, col_2 = st.columns(2)
                with col_1:
                    st.caption(f"Sections: {counts.get('sections', 0)}")
                    st.caption(f"Entities: {counts.get('entities', 0)}")
                    st.caption(f"Candidates: {counts.get('candidate_codes', 0)}")
                    st.caption(f"Validated: {counts.get('validated_codes', 0)}")
                with col_2:
                    st.caption(f"Redactions: {counts.get('redactions', 0)}")
                    st.caption(f"Retrieved: {counts.get('retrieved_context', 0)}")
                    st.caption(f"Alerts: {counts.get('alerts', 0)}")
                    st.caption(f"Explanations: {counts.get('explanations', 0)}")
            provider_routes = diagnostics.get("provider_routes", {})
            if provider_routes:
                st.caption(f"Routes: {provider_routes}")
            models = diagnostics.get("models", {})
            if models:
                st.caption(f"Models: {models}")
            if trace:
                st.markdown("**Trace**")
                for item in trace:
                    st.caption(item)

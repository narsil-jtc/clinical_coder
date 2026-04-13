"""
Code panel component.

Renders grouped code suggestion cards with plain-language review controls.
"""

import streamlit as st

from clinical_coder.config import settings

from ..state_manager import get_decision, get_highlighted_code, set_highlighted_code, update_decision
from .confidence_badge import confidence_badge_html


def _severity_icon(severity: str) -> str:
    icons = {"critical": "&#128308;", "warning": "&#128993;", "info": "&#128309;"}
    return icons.get(severity, "&#9898;")


def _flag_html(flag: dict) -> str:
    severity = flag.get("severity", "info")
    styles = {
        "critical": ("#7f1d1d", "#fee2e2", "#fca5a5"),
        "warning": ("#713f12", "#fef9c3", "#fde047"),
        "info": ("#1e3a5f", "#dbeafe", "#93c5fd"),
    }
    text_col, bg, border = styles.get(severity, ("#374151", "#f3f4f6", "#d1d5db"))
    icon = _severity_icon(severity)
    msg = flag.get("message", "")
    action = flag.get("suggested_action", "")
    return (
        f'<div style="background:{bg};border-left:3px solid {border};'
        f'padding:7px 12px;margin:5px 0;border-radius:0 6px 6px 0;font-size:0.78rem;">'
        f'<div style="font-weight:700;color:{text_col};">{icon} Coding alert</div>'
        f'<div style="color:{text_col};margin-top:2px;">{msg}</div>'
        f'<div style="color:#6b7280;font-style:italic;margin-top:2px;font-size:0.73rem;">{action}</div>'
        f"</div>"
    )


def _section_header_html(label: str, count: int, colour: str) -> str:
    plural = "s" if count != 1 else ""
    return (
        f'<div style="'
        f"display:flex;align-items:center;gap:8px;"
        f"border-left:3px solid {colour};"
        f"padding:4px 10px;margin:10px 0 4px 0;"
        f"background:linear-gradient(90deg,{colour}20 0%,transparent 100%);"
        f'border-radius:0 4px 4px 0;">'
        f'<span style="font-size:0.72rem;font-weight:700;letter-spacing:0.07em;color:{colour};">'
        f"{label}</span>"
        f'<span style="font-size:0.7rem;color:#9ca3af;font-weight:500;">'
        f"{count} code{plural}</span>"
        f"</div>"
    )


def _status_badge(decision: str) -> str:
    status_styles = {
        "accepted": ("&#10003;", "Accepted", "#15803d", "#dcfce7", "#86efac"),
        "rejected": ("&#10007;", "Rejected", "#991b1b", "#fee2e2", "#fca5a5"),
        "modified": ("&#9998;", "Changed", "#1d4ed8", "#dbeafe", "#93c5fd"),
        "pending": ("&#8230;", "Not yet reviewed", "#6b7280", "#f3f4f6", "#d1d5db"),
    }
    icon, label, colour, bg, border = status_styles.get(decision, status_styles["pending"])
    return (
        f'<div style="text-align:right;padding-top:6px;">'
        f'<span style="display:inline-flex;align-items:center;gap:3px;'
        f"background:{bg};color:{colour};border:1px solid {border};"
        f'border-radius:999px;padding:2px 9px;font-size:0.72rem;font-weight:600;">'
        f"{icon} {label}</span></div>"
    )


def render_code_panel(validated_codes: list[dict], explanations: list[dict]) -> None:
    """Render all code suggestion cards."""

    if not validated_codes:
        st.markdown(
            """
        <div style="
            text-align:center;padding:48px 16px;
            color:#9ca3af;border:2px dashed #e2e8f0;
            border-radius:10px;background:#f9fafb;
        ">
            <div style="font-size:2rem;margin-bottom:8px;">&#128203;</div>
            <div style="font-weight:600;font-size:0.9rem;color:#6b7280;">No codes yet</div>
            <div style="font-size:0.8rem;margin-top:4px;">
                Paste a clinical note and click <strong>Run</strong>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return

    exp_map = {e.get("code"): e for e in (explanations or [])}

    high = [c for c in validated_codes if c.get("confidence", 0) >= settings.high_confidence_threshold]
    uncertain = [c for c in validated_codes if c.get("confidence", 0) < settings.high_confidence_threshold]

    if high:
        st.markdown(
            _section_header_html("READY TO CODE", len(high), "#15803d"),
            unsafe_allow_html=True,
        )
        for code_dict in high:
            _render_code_card(code_dict, exp_map)

    if high and uncertain:
        st.divider()

    if uncertain:
        st.markdown(
            _section_header_html("NEEDS YOUR REVIEW", len(uncertain), "#b45309"),
            unsafe_allow_html=True,
        )
        for code_dict in uncertain:
            _render_code_card(code_dict, exp_map)


def _render_code_card(code_dict: dict, exp_map: dict) -> None:
    code = code_dict.get("code", "")
    description = code_dict.get("description", "")
    confidence = code_dict.get("confidence", 0.0)
    evidence_span = code_dict.get("evidence_span", "")
    flags = code_dict.get("validation_flags", [])
    explanation = exp_map.get(code)
    alternative_codes = code_dict.get("alternative_codes") or []

    decision_data = get_decision(code) or {}
    decision = decision_data.get("decision", "pending")
    modified_code = decision_data.get("modified_code")
    is_selected = get_highlighted_code() == code

    with st.container(border=True):
        badge = confidence_badge_html(confidence)
        st.markdown(
            f"{badge} &nbsp;<strong>{code}</strong> &mdash; {description}",
            unsafe_allow_html=True,
        )

        if st.button(
            "View details",
            key=f"view_{code}",
            use_container_width=False,
        ):
            set_highlighted_code(code)
            st.rerun()

        if decision == "modified" and modified_code:
            st.markdown(
                (
                    '<div style="margin-top:4px;color:#1d4ed8;font-size:0.83rem;font-weight:600;">'
                    f"&rarr; Using: {modified_code} instead"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        if evidence_span:
            st.caption(f'Found in your note: "{evidence_span}"')

        for flag in flags:
            st.markdown(_flag_html(flag), unsafe_allow_html=True)

        if explanation or alternative_codes or code_dict.get("requires_additional_code"):
            with st.expander("Why this code was suggested", expanded=is_selected):
                if explanation:
                    if explanation.get("plain_english"):
                        st.markdown(f"**What this means:** {explanation.get('plain_english', '')}")
                    if explanation.get("key_documentation"):
                        st.markdown(
                            f"**Supporting text from your note:** _{explanation.get('key_documentation', '')}_"
                        )
                    if explanation.get("why_not_alternatives"):
                        st.markdown(
                            f"**Why other codes were not chosen:** {explanation.get('why_not_alternatives', '')}"
                        )

                if alternative_codes:
                    st.markdown("**Other codes the AI considered:**")
                    button_columns = st.columns(min(len(alternative_codes), 4))
                    for index, alt_code in enumerate(alternative_codes):
                        column = button_columns[index % len(button_columns)]
                        with column:
                            if st.button(
                                alt_code,
                                key=f"alt_{code}_{alt_code}",
                                use_container_width=True,
                            ):
                                update_decision(code, "modified", alt_code)
                                set_highlighted_code(code)
                                st.rerun()

                if code_dict.get("requires_additional_code") and code_dict.get("suggested_additional_codes"):
                    st.markdown(
                        "**Also needs this code:** "
                        + ", ".join(code_dict["suggested_additional_codes"])
                    )

        col_accept, col_reject, col_status = st.columns([2, 2, 3])

        with col_accept:
            if st.button(
                "Accept",
                key=f"accept_{code}",
                type="primary" if confidence >= settings.high_confidence_threshold else "secondary",
                use_container_width=True,
            ):
                update_decision(code, "accepted")
                set_highlighted_code(code)
                st.rerun()

        with col_reject:
            if st.button("Reject", key=f"reject_{code}", use_container_width=True):
                update_decision(code, "rejected")
                st.rerun()

        with col_status:
            st.markdown(_status_badge(decision), unsafe_allow_html=True)

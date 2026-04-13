"""Code panel component."""

import streamlit as st

from clinical_coder.config import settings
from clinical_coder.ui.theme import empty_state

from ..state_manager import get_decision, get_highlighted_code, set_highlighted_code, update_decision
from .confidence_badge import confidence_badge_html


def _severity_icon(severity: str) -> str:
    return {"critical": "●", "warning": "◐", "info": "○"}.get(severity, "○")


def _flag_html(flag: dict) -> str:
    severity = flag.get("severity", "info")
    styles = {
        "critical": ("#8f3f39", "#fde9e6", "#efbbb3"),
        "warning": ("#8b5a16", "#fff3dd", "#f0cf8a"),
        "info": ("#305f84", "#eaf3fb", "#c9ddeb"),
    }
    text_col, bg, border = styles.get(severity, ("#4b5c67", "#f5f7f8", "#d9e1e5"))
    msg = flag.get("message", "")
    action = flag.get("suggested_action", "")
    return (
        f'<div style="background:{bg};border:1px solid {border};'
        'padding:0.7rem 0.82rem;margin:0.45rem 0;border-radius:14px;">'
        f'<div style="font-weight:700;color:{text_col};font-size:0.76rem;text-transform:uppercase;letter-spacing:0.08em;">{_severity_icon(severity)} Coding alert</div>'
        f'<div style="color:{text_col};margin-top:0.22rem;font-size:0.83rem;line-height:1.5;">{msg}</div>'
        f'<div style="color:#5e7280;margin-top:0.28rem;font-size:0.76rem;line-height:1.45;">{action}</div>'
        "</div>"
    )


def _section_header_html(label: str, count: int, colour: str, copy: str) -> str:
    plural = "s" if count != 1 else ""
    return (
        '<div style="margin:0.3rem 0 0.75rem 0;">'
        f'<div style="text-transform:uppercase;letter-spacing:0.14em;font-size:0.69rem;font-weight:700;color:{colour};">{label}</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:0.8rem;">'
        f'<div style="font-size:0.84rem;color:#5e7280;line-height:1.45;">{copy}</div>'
        f'<div style="font-size:0.76rem;color:#70838f;">{count} code{plural}</div>'
        "</div>"
        "</div>"
    )


def _status_badge(decision: str) -> str:
    status_styles = {
        "accepted": ("Accepted", "#1d6b48", "#e5f5ed", "#b8e1ca"),
        "rejected": ("Rejected", "#9d3e39", "#fde9e6", "#efbbb3"),
        "modified": ("Changed", "#305f84", "#eaf3fb", "#c9ddeb"),
        "pending": ("Awaiting review", "#5e7280", "#f6f4ef", "#ddd6c8"),
    }
    label, colour, bg, border = status_styles.get(decision, status_styles["pending"])
    return (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'background:{bg};color:{colour};border:1px solid {border};'
        'border-radius:999px;padding:0.3rem 0.72rem;font-size:0.73rem;font-weight:700;">'
        f"{label}</span>"
    )


def render_code_panel(validated_codes: list[dict], explanations: list[dict]) -> None:
    """Render all code suggestion cards."""

    if not validated_codes:
        empty_state(
            icon="&#128196;",
            title="The coding deck is empty",
            copy="Once the workflow finds billable diagnoses or procedures, reviewed code cards will appear here.",
        )
        return

    exp_map = {e.get("code"): e for e in (explanations or [])}
    high = [c for c in validated_codes if c.get("confidence", 0) >= settings.high_confidence_threshold]
    uncertain = [c for c in validated_codes if c.get("confidence", 0) < settings.high_confidence_threshold]

    if high:
        st.markdown(
            _section_header_html(
                "Ready to code",
                len(high),
                "#1d6b48",
                "High-confidence suggestions with enough signal for fast review.",
            ),
            unsafe_allow_html=True,
        )
        for code_dict in high:
            _render_code_card(code_dict, exp_map)

    if high and uncertain:
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    if uncertain:
        st.markdown(
            _section_header_html(
                "Needs your judgement",
                len(uncertain),
                "#8b5a16",
                "Suggestions that benefit from a closer read of evidence, flags, or alternatives.",
            ),
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
            f"""
<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.8rem;">
    <div>
        <div style="font-size:1.05rem;font-weight:700;letter-spacing:-0.03em;color:#102330;">{code}</div>
        <div style="font-size:0.9rem;line-height:1.5;color:#233946;margin-top:0.12rem;">{description}</div>
    </div>
    <div style="text-align:right;">{badge}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        meta_cols = st.columns([1.2, 1, 1.2])
        with meta_cols[0]:
            st.markdown(f"**Status**  \n{_status_badge(decision)}", unsafe_allow_html=True)
        with meta_cols[1]:
            st.caption(f"Flags: {len(flags)}")
        with meta_cols[2]:
            if st.button("Focus evidence", key=f"view_{code}", use_container_width=True):
                set_highlighted_code(code)
                st.rerun()

        if decision == "modified" and modified_code:
            st.markdown(
                (
                    '<div style="margin-top:0.45rem;background:#eaf3fb;border:1px solid #c9ddeb;'
                    'color:#305f84;border-radius:14px;padding:0.6rem 0.75rem;font-size:0.82rem;">'
                    f"Using alternate code <strong>{modified_code}</strong> for export."
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        if evidence_span:
            st.markdown(
                (
                    '<div style="margin-top:0.55rem;background:#f7f2e8;border:1px solid #e4d9c5;'
                    'border-radius:14px;padding:0.75rem 0.82rem;">'
                    '<div style="text-transform:uppercase;letter-spacing:0.11em;font-size:0.67rem;'
                    'font-weight:700;color:#8b5a16;margin-bottom:0.24rem;">Evidence from note</div>'
                    f'<div style="font-size:0.84rem;color:#233946;line-height:1.55;">"{evidence_span}"</div>'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        for flag in flags:
            st.markdown(_flag_html(flag), unsafe_allow_html=True)

        if explanation or alternative_codes or code_dict.get("requires_additional_code"):
            with st.expander("Review rationale", expanded=is_selected):
                if explanation:
                    if explanation.get("plain_english"):
                        st.markdown(f"**Clinical interpretation**  \n{explanation.get('plain_english', '')}")
                    if explanation.get("key_documentation"):
                        st.markdown(f"**Supporting text**  \n_{explanation.get('key_documentation', '')}_")
                    if explanation.get("why_not_alternatives"):
                        st.markdown(f"**Why not alternatives**  \n{explanation.get('why_not_alternatives', '')}")

                if alternative_codes:
                    st.markdown("**Alternative codes considered**")
                    button_columns = st.columns(min(len(alternative_codes), 4))
                    for index, alt_code in enumerate(alternative_codes):
                        with button_columns[index % len(button_columns)]:
                            if st.button(alt_code, key=f"alt_{code}_{alt_code}", use_container_width=True):
                                update_decision(code, "modified", alt_code)
                                set_highlighted_code(code)
                                st.rerun()

                if code_dict.get("requires_additional_code") and code_dict.get("suggested_additional_codes"):
                    st.markdown(
                        "**Suggested companion codes**  \n" + ", ".join(code_dict["suggested_additional_codes"])
                    )

        col_accept, col_reject = st.columns(2)
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

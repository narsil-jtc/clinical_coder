"""Note viewer component."""

import streamlit as st

from clinical_coder.ui.theme import status_banner

from ..state_manager import get_highlighted_code


def _highlight_span(text: str, span: str) -> str:
    """Wrap the evidence span in the note text with a highlight mark."""
    if not span or span not in text:
        return text
    return text.replace(
        span,
        (
            '<mark style="background:#fde7a7;color:#102330;border-radius:7px;'
            'padding:0.08rem 0.18rem;box-shadow:0 0 0 1px rgba(139,90,22,0.10);">'
            f"{span}</mark>"
        ),
        1,
    )


def render_note_viewer(sections: dict[str, str], evidence_spans: dict[str, str]) -> None:
    """Render the clinical note in a tabbed view."""

    if not sections:
        status_banner("No clinical note loaded yet. Paste a note in the workspace and run the workflow.", tone="warning")
        return

    highlighted_code = get_highlighted_code()
    active_span = evidence_spans.get(highlighted_code, "") if highlighted_code else ""

    if active_span:
        status_banner(
            f"<strong>Evidence focus:</strong> the note is highlighting supporting text for the selected code.",
            tone="warning",
        )

    priority = [
        "assessment", "plan", "discharge",
        "presenting_complaint", "history", "past_medical_history",
        "investigations", "examination", "medications", "allergies", "body",
    ]
    tab_labels = [s for s in priority if s in sections]
    tab_labels += [s for s in sections if s not in priority]

    if not tab_labels:
        st.text_area("Note", value=list(sections.values())[0], height=500, disabled=True)
        return

    tabs = st.tabs([lbl.replace("_", " ").title() for lbl in tab_labels])
    for tab, label in zip(tabs, tab_labels):
        with tab:
            text = sections[label]
            html_text = _highlight_span(text, active_span) if active_span else text
            st.markdown(
                (
                    '<div style="background:rgba(255,255,255,0.85);border:1px solid rgba(16,35,48,0.09);'
                    'border-radius:18px;padding:1rem 1rem 1.05rem 1rem;box-shadow:0 8px 24px rgba(16,35,48,0.05);">'
                    '<div style="text-transform:uppercase;letter-spacing:0.12em;font-size:0.67rem;font-weight:700;'
                    f'color:#1e6b73;margin-bottom:0.55rem;">{label.replace("_", " ")}</div>'
                    '<div style="font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;'
                    'font-size:0.84rem;white-space:pre-wrap;line-height:1.74;color:#102330;">'
                    f"{html_text}</div></div>"
                ),
                unsafe_allow_html=True,
            )

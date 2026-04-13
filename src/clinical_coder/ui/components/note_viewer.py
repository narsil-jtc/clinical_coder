"""
Note viewer component.

Displays the clinical note with:
- Section tabs for navigation
- Evidence span highlighting when a code is hovered/selected
"""
import streamlit as st
from ..state_manager import get_highlighted_code


def _highlight_span(text: str, span: str) -> str:
    """Wrap the evidence span in the note text with a highlight mark."""
    if not span or span not in text:
        return text
    highlighted = text.replace(
        span,
        f'<mark style="background:#fff3cd;border-radius:3px;padding:1px 2px;">{span}</mark>',
        1,
    )
    return highlighted


def render_note_viewer(sections: dict[str, str], evidence_spans: dict[str, str]) -> None:
    """
    Render the clinical note in a tabbed view.

    Args:
        sections: dict of {section_label: section_text}
        evidence_spans: dict of {code: evidence_span} — text to highlight per selected code
    """
    if not sections:
        st.info("No clinical note loaded. Paste a note in the left panel and click Run.")
        return

    highlighted_code = get_highlighted_code()
    active_span = evidence_spans.get(highlighted_code, "") if highlighted_code else ""

    # Reorder tabs: most clinically relevant first
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
            # Use HTML rendering to show highlights
            st.markdown(
                f'<div style="'
                f'font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;'
                f"font-size:0.83rem;"
                f"white-space:pre-wrap;"
                f"line-height:1.7;"
                f"padding:12px 16px;"
                f"background:#fafafa;"
                f"border:1px solid #e2e8f0;"
                f"border-radius:8px;"
                f"max-height:520px;"
                f"overflow-y:auto;"
                f'color:#1a202c;">'
                f"{html_text}"
                f"</div>",
                unsafe_allow_html=True,
            )

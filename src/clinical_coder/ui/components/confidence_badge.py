"""
Confidence badge component.

Renders a pill-style colour-coded badge based on the confidence score:
  GREEN  ≥ 0.80 — high confidence, one-click accept available
  AMBER  0.50–0.79 — moderate, reviewer should read evidence before accepting
  RED    < 0.50 — low confidence, treat with caution

Returns an HTML string for use with st.markdown(..., unsafe_allow_html=True).
"""
from clinical_coder.config import settings


def confidence_badge_html(confidence: float) -> str:
    """Return a pill-style HTML badge for the given confidence score."""
    pct = int(confidence * 100)

    if confidence >= settings.high_confidence_threshold:
        colour, bg, border, label, icon = "#14532d", "#dcfce7", "#86efac", "HIGH", "●"
    elif confidence >= settings.low_confidence_threshold:
        colour, bg, border, label, icon = "#713f12", "#fef9c3", "#fde047", "MED", "◐"
    else:
        colour, bg, border, label, icon = "#7f1d1d", "#fee2e2", "#fca5a5", "LOW", "○"

    return (
        f'<span style="'
        f"display:inline-flex;align-items:center;gap:4px;"
        f"background:{bg};color:{colour};"
        f"border:1px solid {border};"
        f"border-radius:999px;"
        f"padding:2px 10px;"
        f"font-size:0.72rem;font-weight:700;font-family:monospace;"
        f'white-space:nowrap;">'
        f"{icon} {label} {pct}%</span>"
    )

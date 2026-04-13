"""Confidence badge component."""

from clinical_coder.config import settings


def confidence_badge_html(confidence: float) -> str:
    """Return a pill-style HTML badge for the given confidence score."""

    pct = int(confidence * 100)

    if confidence >= settings.high_confidence_threshold:
        colour, bg, border, label, icon = "#1d6b48", "#e5f5ed", "#b8e1ca", "High confidence", "●"
    elif confidence >= settings.low_confidence_threshold:
        colour, bg, border, label, icon = "#8b5a16", "#fff3dd", "#f0cf8a", "Needs review", "◐"
    else:
        colour, bg, border, label, icon = "#9d3e39", "#fde9e6", "#efbbb3", "Low confidence", "○"

    return (
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'background:{bg};color:{colour};border:1px solid {border};'
        'border-radius:999px;padding:0.3rem 0.78rem;font-size:0.73rem;'
        'font-weight:700;letter-spacing:0.02em;white-space:nowrap;">'
        f"{icon} {label} {pct}%</span>"
    )

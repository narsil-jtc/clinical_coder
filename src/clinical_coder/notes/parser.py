"""Rule-based clinical note section parsing."""

from __future__ import annotations

import re

_SECTION_PATTERNS: list[tuple[str, str]] = [
    ("presenting_complaint", r"\b(presenting\s+complaint|chief\s+complaint|reason\s+for\s+(admission|attendance))\b"),
    ("past_medical_history", r"\b(past\s+medical\s+history|pmh|background)\b"),
    ("history", r"\b(history\s+of\s+presenting\s+(complaint|illness)|hpc|history)\b"),
    ("medications", r"\b(medications?|drugs?|current\s+medications?|drug\s+history)\b"),
    ("allergies", r"\b(allerg(ies|y))\b"),
    ("examination", r"\b(examination|on\s+examination|clinical\s+findings?|o/e)\b"),
    ("investigations", r"\b(investigations?|results?|bloods?|imaging|ecg|echo)\b"),
    ("assessment", r"\b(assessment(\s+and\s+plan)?|impression|differential|problem\s+list)\b"),
    ("plan", r"\b(plan|management|treatment)\b"),
    ("discharge", r"\b(discharge\s+(summary|plan|medications?|advice))\b"),
    ("follow_up", r"\b(follow[\s\-]?up)\b"),
]

_HEADER_RE = re.compile(r"^(?P<header>[A-Z][A-Za-z\s/\-()]{2,60}):?\s*$", re.MULTILINE)


def _classify_header(header_text: str) -> str:
    header = header_text.lower().strip().rstrip(":")
    for label, pattern in _SECTION_PATTERNS:
        if re.search(pattern, header, re.IGNORECASE):
            return label
    return header.replace(" ", "_")


def parse_sections(raw_note: str) -> dict[str, str]:
    """Split a clinical note into canonical labeled sections."""

    sections: dict[str, str] = {}
    matches = list(_HEADER_RE.finditer(raw_note))
    if not matches:
        return {"body": raw_note.strip()}

    preamble = raw_note[: matches[0].start()].strip()
    if preamble:
        sections["body"] = preamble

    for index, match in enumerate(matches):
        label = _classify_header(match.group("header").strip())
        text_start = match.end()
        text_end = matches[index + 1].start() if index + 1 < len(matches) else len(raw_note)
        section_text = raw_note[text_start:text_end].strip()
        if label in sections:
            sections[label] = sections[label] + "\n\n" + section_text
        else:
            sections[label] = section_text

    return sections

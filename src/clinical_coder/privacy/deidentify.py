"""Local text minimisation and lightweight de-identification."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")
_DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
_ID_RE = re.compile(r"\b(?:NHS|MRN|PATIENT|ID)[:\s-]*[A-Z0-9-]{4,}\b", re.IGNORECASE)


@dataclass
class DeidentificationResult:
    text: str
    redacted_items: list[dict] = field(default_factory=list)


def deidentify_text(text: str) -> DeidentificationResult:
    """Redact obvious identifiers while preserving clinical meaning."""

    redacted_items: list[dict] = []
    result = text
    patterns = [
        (_ID_RE, "[IDENTIFIER]", "identifier"),
        (_DATE_RE, "[DATE]", "date"),
        (_NAME_RE, "[PERSON]", "name"),
    ]
    for pattern, replacement, label in patterns:
        matches = list(pattern.finditer(result))
        if matches:
            for match in matches:
                redacted_items.append({"type": label, "value": match.group(0)})
            result = pattern.sub(replacement, result)
    return DeidentificationResult(text=result, redacted_items=redacted_items)


def minimise_sections(sections: dict[str, str], priority: list[str], max_chars: int) -> str:
    """Select only the highest-value sections before any external reasoning."""

    blocks: list[str] = []
    total = 0
    for label in priority:
        text = sections.get(label, "").strip()
        if not text:
            continue
        block = f"[{label.upper()}]\n{text}"
        if total + len(block) > max_chars:
            remaining = max_chars - total
            if remaining > 100:
                blocks.append(block[:remaining] + "...")
            break
        blocks.append(block)
        total += len(block)
    return "\n\n".join(blocks)

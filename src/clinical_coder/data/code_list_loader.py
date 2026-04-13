"""Backward-compatible loading on top of normalized XML terminology records."""

from __future__ import annotations

from pathlib import Path

from clinical_coder.terminology.repository import load_terminology_bundle


def load_code_list(path: str | Path) -> dict[str, str]:
    """Return a legacy `{code: description}` mapping for the active XML terminology file."""

    bundle = load_terminology_bundle(str(Path(path).resolve()))
    return {record.code: record.title for record in bundle.records if record.billable}

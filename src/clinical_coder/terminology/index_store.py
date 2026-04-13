"""Helpers for retrieval document and collection naming."""

from __future__ import annotations

import re

from clinical_coder.terminology.models import TerminologyRecord


def build_document(record: TerminologyRecord) -> str:
    """Build the text document stored in the retrieval index."""

    notes = " ".join(record.notes)
    return " - ".join(part for part in [record.code, record.title, notes] if part).strip()


def terminology_collection_name(source_id: str, edition: str) -> str:
    """Return a stable Chroma collection name for one terminology source."""

    raw = f"icd10_codes__{source_id}__{edition}".lower()
    return re.sub(r"[^a-z0-9_-]+", "_", raw).strip("_")

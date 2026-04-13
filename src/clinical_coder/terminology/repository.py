"""Cached terminology repository for XML-based WHO and UK ICD-10 sources."""

from __future__ import annotations

import functools
from pathlib import Path

from clinical_coder.config import settings
from clinical_coder.ingestion.uk_claml import load_uk_claml_bundle
from clinical_coder.ingestion.who_claml import load_who_claml_bundle
from clinical_coder.terminology.models import TerminologyBundle, TerminologyRecord


def _detect_bundle(path: Path) -> TerminologyBundle:
    suffix = path.suffix.lower()
    if suffix != ".xml":
        raise ValueError(f"Unsupported terminology file: {path}. Only XML terminology bundles are supported.")
    if "uk" in path.name.lower():
        return load_uk_claml_bundle(path)
    return load_who_claml_bundle(path)


@functools.lru_cache(maxsize=4)
def load_terminology_bundle(path: str | None = None) -> TerminologyBundle:
    """Load and cache the active XML terminology source."""

    source_path = Path(path or settings.icd10_code_list_path).resolve()
    return _detect_bundle(source_path)


def get_terminology_scope_label(path: str | None = None) -> str:
    """Return the human-readable scope label for the active terminology source."""

    bundle = load_terminology_bundle(path)
    return f"{bundle.edition} ({bundle.source_id})"


def get_record_map(path: str | None = None) -> dict[str, TerminologyRecord]:
    """Convenience map keyed by code."""

    bundle = load_terminology_bundle(path)
    return {record.code: record for record in bundle.records}

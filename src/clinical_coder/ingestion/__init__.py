"""Terminology ingestion adapters."""

from .who_claml import load_who_claml_bundle
from .uk_claml import load_uk_claml_bundle

__all__ = ["load_who_claml_bundle", "load_uk_claml_bundle"]

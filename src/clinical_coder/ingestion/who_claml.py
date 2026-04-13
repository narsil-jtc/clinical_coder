"""WHO ICD ClaML adapter."""

from pathlib import Path

from .claml import load_claml_bundle


def load_who_claml_bundle(path: str | Path):
    return load_claml_bundle(path=path, source_id="who_icd10", edition="WHO ICD-10")

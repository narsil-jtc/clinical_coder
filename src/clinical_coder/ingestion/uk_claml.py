"""UK ICD ClaML adapter.

The current UK adapter intentionally reuses the ClaML parser so a future
UK-specific schema variation only needs to change this file.
"""

from pathlib import Path

from .claml import load_claml_bundle


def load_uk_claml_bundle(path: str | Path):
    return load_claml_bundle(path=path, source_id="uk_icd10_5e", edition="UK ICD-10 5th Edition")

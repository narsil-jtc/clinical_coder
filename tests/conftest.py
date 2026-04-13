"""
Pytest configuration and shared fixtures.
"""
import json
from pathlib import Path
import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_notes() -> list[dict]:
    """Load the sample notes fixture."""
    path = FIXTURES_DIR / "sample_notes.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def stemi_note(sample_notes) -> dict:
    return next(n for n in sample_notes if n["note_id"] == "TEST-STEMI-001")


@pytest.fixture
def hf_note(sample_notes) -> dict:
    return next(n for n in sample_notes if n["note_id"] == "TEST-HF-001")


@pytest.fixture
def simple_sections() -> dict[str, str]:
    return {
        "assessment": (
            "1. Anterior STEMI — confirmed on ECG.\n"
            "2. Type 2 diabetes mellitus — HbA1c elevated."
        ),
        "plan": "PCI to LAD performed. Dual antiplatelet therapy.",
    }

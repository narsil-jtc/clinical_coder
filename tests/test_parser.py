"""
Tests for the parser node — no LLM calls required.
"""
from clinical_coder.notes.parser import parse_sections


def test_parse_assessment_and_plan():
    note = """\
ASSESSMENT AND PLAN:
1. Anterior STEMI — confirmed on ECG.
2. Type 2 diabetes.

DISCHARGE MEDICATIONS:
Aspirin 75mg daily.
"""
    sections = parse_sections(note)
    assert "assessment" in sections
    assert "STEMI" in sections["assessment"]


def test_parse_no_headers():
    note = "Patient presented with chest pain. Ecg showed STEMI."
    sections = parse_sections(note)
    # Should fall back to "body"
    assert "body" in sections
    assert "STEMI" in sections["body"]


def test_parse_history_section():
    note = """\
PAST MEDICAL HISTORY:
- Hypertension
- Type 2 diabetes

PRESENTING COMPLAINT:
Chest pain.
"""
    sections = parse_sections(note)
    assert "past_medical_history" in sections
    assert "Hypertension" in sections["past_medical_history"]
    assert "presenting_complaint" in sections


def test_parse_multiple_sections():
    note = """\
PRESENTING COMPLAINT:
Chest pain.

HISTORY:
Two-day history of dyspnoea.

ASSESSMENT AND PLAN:
1. Heart failure.
"""
    sections = parse_sections(note)
    assert len(sections) >= 2


def test_parse_returns_dict():
    note = "Some clinical text."
    result = parse_sections(note)
    assert isinstance(result, dict)
    assert len(result) > 0

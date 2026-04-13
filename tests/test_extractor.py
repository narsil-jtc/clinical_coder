"""
Tests for the extraction task utilities.
"""

from clinical_coder.reasoning.tasks.extraction import deduplicate_entities


def test_deduplicate_removes_exact_duplicates():
    entities = [
        {"normalized_term": "myocardial infarction", "entity_type": "diagnosis"},
        {"normalized_term": "myocardial infarction", "entity_type": "diagnosis"},
    ]
    result = deduplicate_entities(entities)
    assert len(result) == 1


def test_deduplicate_keeps_different_types():
    entities = [
        {"normalized_term": "aspirin", "entity_type": "procedure"},
        {"normalized_term": "aspirin", "entity_type": "modifier"},
    ]
    result = deduplicate_entities(entities)
    assert len(result) == 2


def test_deduplicate_case_insensitive():
    entities = [
        {"normalized_term": "Myocardial Infarction", "entity_type": "diagnosis"},
        {"normalized_term": "myocardial infarction", "entity_type": "diagnosis"},
    ]
    result = deduplicate_entities(entities)
    assert len(result) == 1


def test_deduplicate_empty_list():
    assert deduplicate_entities([]) == []


def test_deduplicate_preserves_order():
    entities = [
        {"normalized_term": "heart failure", "entity_type": "diagnosis"},
        {"normalized_term": "atrial fibrillation", "entity_type": "diagnosis"},
        {"normalized_term": "heart failure", "entity_type": "diagnosis"},
    ]
    result = deduplicate_entities(entities)
    assert len(result) == 2
    assert result[0]["normalized_term"] == "heart failure"
    assert result[1]["normalized_term"] == "atrial fibrillation"

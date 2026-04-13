"""
Tests for deterministic validation helpers.
"""

from clinical_coder.rules.validator import (
    _check_code_existence,
    _check_excludes1,
    _check_header_code,
    _check_laterality,
)


def test_existence_valid_code():
    valid_codes = {"I21.0", "E11.2", "N17.9"}
    assert _check_code_existence("I21.0", valid_codes) is None


def test_existence_invalid_code():
    valid_codes = {"I21.0", "E11.2"}
    flag = _check_code_existence("ZZZZ.99", valid_codes)
    assert flag is not None
    assert flag["severity"] == "critical"
    assert "ZZZZ.99" in flag["message"]


def test_existence_local_extension_hint_when_category_exists():
    valid_codes = {"E11", "E11.2", "E11.8"}
    flag = _check_code_existence("E11.99", valid_codes, terminology_scope="WHO ICD-10 2019 (who_icd10_2019)")
    assert flag is not None
    assert "exact subcode does not" in flag["message"]
    assert "different ICD-10 edition" in flag["suggested_action"]


def test_existence_empty_set_skips_check():
    assert _check_code_existence("ANYTHING", set()) is None


def test_header_code_flagged():
    flag = _check_header_code("I21", header_codes=["I21", "E11"])
    assert flag is not None
    assert flag["severity"] == "critical"
    assert "header" in flag["message"].lower()


def test_billable_code_not_flagged():
    flag = _check_header_code("I21.0", header_codes=["I21", "E11"])
    assert flag is None


def test_header_code_empty_list():
    flag = _check_header_code("I21", header_codes=[])
    assert flag is None


def test_excludes1_conflict_detected():
    pairs = [
        {
            "rule_id": "EX1-E10-E11",
            "code_a_prefix": "E10",
            "code_b_prefix": "E11",
            "description": "T1DM and T2DM cannot be co-coded",
        }
    ]
    all_codes = {"E10.9", "E11.2"}
    flag = _check_excludes1("E10.9", all_codes, pairs)
    assert flag is not None
    assert flag["severity"] == "critical"
    assert "EX1-E10-E11" == flag["rule_id"]


def test_excludes1_no_conflict():
    pairs = [
        {
            "rule_id": "EX1-E10-E11",
            "code_a_prefix": "E10",
            "code_b_prefix": "E11",
            "description": "T1DM and T2DM",
        }
    ]
    all_codes = {"I21.0", "E11.2"}
    flag = _check_excludes1("I21.0", all_codes, pairs)
    assert flag is None


def test_excludes1_b_triggers_when_a_present():
    pairs = [
        {
            "rule_id": "EX1-I21-I22",
            "code_a_prefix": "I21",
            "code_b_prefix": "I22",
            "description": "Cannot code together",
        }
    ]
    all_codes = {"I21.0", "I22.9"}
    flag = _check_excludes1("I22.9", all_codes, pairs)
    assert flag is not None


def test_laterality_flag_when_unspecified():
    entities = [{"normalized_term": "knee replacement", "laterality": "unspecified"}]
    candidates = [{"code": "M17.11", "supporting_entity": "knee replacement"}]
    prefixes = ["M17"]
    flags = _check_laterality(entities, candidates, prefixes)
    assert len(flags) == 1
    assert flags[0]["severity"] == "warning"


def test_no_laterality_flag_when_specified():
    entities = [{"normalized_term": "knee replacement", "laterality": "right"}]
    candidates = [{"code": "M17.11", "supporting_entity": "knee replacement"}]
    prefixes = ["M17"]
    flags = _check_laterality(entities, candidates, prefixes)
    assert len(flags) == 0


def test_no_laterality_flag_for_non_laterality_code():
    entities = [{"normalized_term": "heart failure", "laterality": "unspecified"}]
    candidates = [{"code": "I50.9", "supporting_entity": "heart failure"}]
    prefixes = ["M17", "S72"]
    flags = _check_laterality(entities, candidates, prefixes)
    assert len(flags) == 0

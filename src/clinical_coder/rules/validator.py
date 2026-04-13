"""Deterministic validation logic over normalized terminology records."""

from __future__ import annotations

import json
import logging

from clinical_coder.config import settings
from clinical_coder.terminology.repository import load_terminology_bundle

logger = logging.getLogger(__name__)


def load_rules(path: str | None = None) -> dict:
    """Load validation rules JSON."""

    rules_path = settings.validation_rules_file if path is None else settings.project_root / path
    if not rules_path.exists():
        logger.warning("Validation rules file not found at %s", rules_path)
        return {}
    return json.loads(rules_path.read_text(encoding="utf-8"))


def _matches_known_category_without_exact_code(code: str, valid_codes: dict[str, object]) -> bool:
    stem = code.split(".", 1)[0]
    return any(existing == stem or existing.startswith(f"{stem}.") for existing in valid_codes)


def _check_code_existence(
    code: str,
    valid_codes: dict[str, object],
    terminology_scope: str = "",
) -> dict | None:
    if not valid_codes:
        return None
    if code not in valid_codes:
        if _matches_known_category_without_exact_code(code, valid_codes):
            scope_text = terminology_scope or "the loaded terminology source"
            return {
                "code": code,
                "rule_id": "EXISTENCE-001",
                "severity": "critical",
                "message": (
                    f"Code '{code}' is not present in {scope_text}. "
                    "The category exists, but this exact subcode does not."
                ),
                "suggested_action": (
                    "Check for the equivalent code in the active terminology source. "
                    "This often indicates a different ICD-10 edition or local extension."
                ),
            }
        return {
            "code": code,
            "rule_id": "EXISTENCE-001",
            "severity": "critical",
            "message": (
                f"Code '{code}' not found in "
                f"{terminology_scope or 'the loaded terminology source'}."
            ),
            "suggested_action": "Verify the code against the configured ICD source and edition.",
        }
    return None


def _check_header_code(code: str, header_codes: list[str]) -> dict | None:
    if code in header_codes:
        return {
            "code": code,
            "rule_id": "BILLABLE-001",
            "severity": "critical",
            "message": f"'{code}' is a header/category code and is not billable.",
            "suggested_action": "Replace with a more specific child code.",
        }
    return None


def _check_excludes1(code: str, all_codes: set[str], excludes1_pairs: list[dict]) -> dict | None:
    for pair in excludes1_pairs:
        a_prefix = pair.get("code_a_prefix", "")
        b_prefix = pair.get("code_b_prefix", "")
        if code.startswith(a_prefix):
            conflicts = [other for other in all_codes if other.startswith(b_prefix)]
        elif code.startswith(b_prefix):
            conflicts = [other for other in all_codes if other.startswith(a_prefix)]
        else:
            conflicts = []
        if conflicts:
            return {
                "code": code,
                "rule_id": pair.get("rule_id", "EXCL1-001"),
                "severity": "critical",
                "message": (
                    f"Excludes-1 conflict: '{code}' cannot be coded with {', '.join(conflicts)}. "
                    f"{pair.get('description', '')}"
                ).strip(),
                "suggested_action": "Review the documentation and choose the correct mutually exclusive code.",
            }
    return None


def _check_laterality(entities: list[dict], candidates: list[dict], laterality_prefixes: list[str]) -> list[dict]:
    entity_map = {entity.get("normalized_term", "").lower(): entity for entity in entities}
    flags: list[dict] = []
    for candidate in candidates:
        code = candidate.get("code", "")
        if not any(code.startswith(prefix) for prefix in laterality_prefixes):
            continue
        entity = entity_map.get(candidate.get("supporting_entity", "").lower(), {})
        if entity.get("laterality", "unspecified") == "unspecified":
            flags.append(
                {
                    "code": code,
                    "rule_id": "LAT-001",
                    "severity": "warning",
                    "message": f"Code '{code}' commonly requires laterality but the extracted evidence is unspecified.",
                    "suggested_action": "Check the source note for left/right/bilateral detail.",
                }
            )
    return flags


def validate_candidates(
    candidates: list[dict],
    entities: list[dict],
    code_list_path: str | None = None,
) -> tuple[list[dict], list[dict]]:
    """Validate candidate codes and return per-code and flattened flags."""

    if not candidates:
        return [], []

    rules = load_rules()
    bundle = load_terminology_bundle(code_list_path)
    records = {record.code: record for record in bundle.records}
    terminology_scope = f"{bundle.edition} ({bundle.source_id})"
    excludes1_pairs = rules.get("excludes1_pairs", [])
    laterality_prefixes = rules.get("laterality_required_prefixes", [])

    all_candidate_codes = {candidate.get("code", "") for candidate in candidates}
    validated_codes: list[dict] = []
    all_flags: list[dict] = []

    for candidate in candidates:
        code = candidate.get("code", "")
        flags: list[dict] = []

        record = records.get(code)
        flag = _check_code_existence(code, records, terminology_scope=terminology_scope)
        if flag:
            flags.append(flag)
        if record and not record.billable:
            header_flag = _check_header_code(code, [code])
            if header_flag:
                flags.append(header_flag)

        exclude_flag = _check_excludes1(code, all_candidate_codes, excludes1_pairs)
        if exclude_flag:
            flags.append(exclude_flag)

        validated_codes.append({**candidate, "validation_flags": flags})
        all_flags.extend(flags)

    for flag in _check_laterality(entities, validated_codes, laterality_prefixes):
        for validated in validated_codes:
            if validated.get("code") != flag["code"]:
                continue
            validated["validation_flags"].append(flag)
            all_flags.append(flag)

    return validated_codes, all_flags

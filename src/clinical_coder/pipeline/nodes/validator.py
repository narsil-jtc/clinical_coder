"""Legacy compatibility wrapper for deterministic validation."""

from clinical_coder.reasoning.state import WorkflowState
from clinical_coder.rules.validator import (
    _check_code_existence,
    _check_excludes1,
    _check_header_code,
    _check_laterality,
    validate_candidates,
)


def run(state: WorkflowState) -> WorkflowState:
    validated_codes, all_flags = validate_candidates(
        state.get("candidate_codes", []),
        state.get("entities", []),
        code_list_path=state.get("icd10_code_list_path"),
    )
    return {
        **state,
        "validated_codes": validated_codes,
        "all_validation_flags": all_flags,
        "errors": list(state.get("errors", [])),
    }


__all__ = [
    "_check_code_existence",
    "_check_excludes1",
    "_check_header_code",
    "_check_laterality",
    "run",
]

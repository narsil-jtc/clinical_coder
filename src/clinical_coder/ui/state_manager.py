"""Streamlit session state manager."""

import streamlit as st

from clinical_coder.reasoning.state import WorkflowState

_WORKFLOW_RESULT_KEY = "workflow_result"
_LEGACY_PIPELINE_RESULT_KEY = "pipeline_result"


def get_workflow_result() -> WorkflowState | None:
    """Return the current workflow result, with legacy fallback."""

    return st.session_state.get(_WORKFLOW_RESULT_KEY) or st.session_state.get(_LEGACY_PIPELINE_RESULT_KEY)


def set_workflow_result(result: WorkflowState) -> None:
    """Persist the current workflow result and reset review state."""

    st.session_state[_WORKFLOW_RESULT_KEY] = result
    st.session_state[_LEGACY_PIPELINE_RESULT_KEY] = result
    st.session_state["review_decisions"] = {}
    st.session_state["flags_acknowledged"] = set()


def clear_workflow_result() -> None:
    """Clear current workflow and review state."""

    st.session_state.pop(_WORKFLOW_RESULT_KEY, None)
    st.session_state.pop(_LEGACY_PIPELINE_RESULT_KEY, None)
    st.session_state.pop("review_decisions", None)
    st.session_state.pop("flags_acknowledged", None)


def get_review_decisions() -> dict[str, str]:
    return st.session_state.get("review_decisions", {})


def update_decision(code: str, decision: str, modified_code: str | None = None) -> None:
    if "review_decisions" not in st.session_state:
        st.session_state["review_decisions"] = {}
    st.session_state["review_decisions"][code] = {
        "decision": decision,
        "modified_code": modified_code,
    }


def get_decision(code: str) -> dict | None:
    return st.session_state.get("review_decisions", {}).get(code)


def get_acknowledged_flags() -> set[str]:
    return st.session_state.get("flags_acknowledged", set())


def acknowledge_flag(rule_id: str) -> None:
    if "flags_acknowledged" not in st.session_state:
        st.session_state["flags_acknowledged"] = set()
    st.session_state["flags_acknowledged"].add(rule_id)


def get_highlighted_code() -> str | None:
    return st.session_state.get("highlighted_code")


def set_highlighted_code(code: str | None) -> None:
    st.session_state["highlighted_code"] = code


def get_review_summary() -> dict:
    """Return counts of accepted / rejected / modified / pending decisions."""

    decisions = get_review_decisions()
    result = get_workflow_result() or {}
    all_codes = [c.get("code") for c in result.get("validated_codes", [])]

    counts = {"accepted": 0, "rejected": 0, "modified": 0, "pending": 0}
    for code in all_codes:
        dec = decisions.get(code, {}).get("decision", "pending")
        counts[dec] = counts.get(dec, 0) + 1
    return counts


def all_flags_acknowledged() -> bool:
    """True when all validation flags have been acknowledged by the reviewer."""

    result = get_workflow_result() or {}
    all_flags = result.get("all_validation_flags", [])
    if not all_flags:
        return True
    acknowledged = get_acknowledged_flags()
    return all(flag.get("rule_id") in acknowledged for flag in all_flags)


# Backward-compatible aliases while the remaining legacy surface is retired.
get_pipeline_result = get_workflow_result
set_pipeline_result = set_workflow_result
clear_pipeline_result = clear_workflow_result

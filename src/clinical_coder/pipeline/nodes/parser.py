"""Legacy compatibility wrapper for note parsing."""

from clinical_coder.notes.parser import parse_sections
from clinical_coder.reasoning.state import WorkflowState


def run(state: WorkflowState) -> WorkflowState:
    raw = state.get("raw_note", "")
    if not raw:
        return {**state, "sections": {}, "errors": state.get("errors", []) + ["Parser: raw_note is empty"]}
    return {**state, "sections": parse_sections(raw)}


__all__ = ["parse_sections", "run"]

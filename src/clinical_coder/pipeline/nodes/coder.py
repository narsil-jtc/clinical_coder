"""Legacy compatibility wrapper for the coding task."""

from clinical_coder.reasoning.providers.ollama import OllamaReasoningProvider
from clinical_coder.reasoning.state import WorkflowState
from clinical_coder.reasoning.tasks.coding import format_retrieved_context, run_coding


def run(state: WorkflowState) -> WorkflowState:
    entities: list[dict] = state.get("entities", [])
    retrieved: list[dict] = state.get("retrieved_context", [])
    errors: list[str] = list(state.get("errors", []))

    if not entities:
        errors.append("Coder: no entities to code - extractor may have returned nothing")
        return {**state, "candidate_codes": [], "missing_specificity_flags": [], "errors": errors}

    provider = OllamaReasoningProvider(
        num_ctx=state.get("llm_num_ctx", 4096),
        num_predict=state.get("llm_num_predict", 2048),
        keep_alive=state.get("llm_keep_alive", "30m"),
    )

    try:
        candidate_codes, missing_specificity_flags, coding_model = run_coding(provider, entities, retrieved)
        return {
            **state,
            "candidate_codes": candidate_codes,
            "missing_specificity_flags": missing_specificity_flags,
            "coding_model": coding_model,
            "_retry_count": state.get("_retry_count", 0) + 1,
            "errors": errors,
        }
    except Exception as exc:
        errors.append(f"Coder: LLM call failed: {exc}")
        return {
            **state,
            "candidate_codes": [],
            "missing_specificity_flags": [],
            "errors": errors,
        }


__all__ = ["format_retrieved_context", "run"]

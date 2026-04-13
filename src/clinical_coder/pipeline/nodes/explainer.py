"""Legacy compatibility wrapper for the explanation task."""

from clinical_coder.reasoning.providers.ollama import OllamaReasoningProvider
from clinical_coder.reasoning.state import WorkflowState
from clinical_coder.reasoning.tasks.explanation import build_note_excerpt, run_explanation


def run(state: WorkflowState) -> WorkflowState:
    candidates: list[dict] = state.get("candidate_codes", [])
    sections: dict[str, str] = state.get("sections", {})
    errors: list[str] = list(state.get("errors", []))

    if not candidates:
        return {**state, "explanations": [], "errors": errors}

    provider = OllamaReasoningProvider(
        num_ctx=state.get("llm_num_ctx", 4096),
        num_predict=state.get("llm_num_predict", 2048),
        keep_alive=state.get("llm_keep_alive", "30m"),
    )

    try:
        explanations = run_explanation(provider, candidates, build_note_excerpt(sections))
        return {**state, "explanations": explanations, "errors": errors}
    except Exception as exc:
        errors.append(f"Explainer: LLM call failed: {exc}")
        return {**state, "explanations": [], "errors": errors}


__all__ = ["build_note_excerpt", "run"]

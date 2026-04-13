"""Legacy compatibility wrapper for the extraction task."""

from clinical_coder.reasoning.providers.ollama import OllamaReasoningProvider
from clinical_coder.reasoning.state import WorkflowState
from clinical_coder.reasoning.tasks.extraction import (
    build_extraction_text,
    deduplicate_entities,
    run_extraction,
)


def run(state: WorkflowState) -> WorkflowState:
    sections: dict[str, str] = state.get("sections", {})
    errors: list[str] = list(state.get("errors", []))

    if not sections:
        errors.append("Extractor: no sections available - parser may have failed")
        return {**state, "entities": [], "errors": errors}

    payload = build_extraction_text(sections)
    if not payload.strip():
        errors.append("Extractor: all sections are empty")
        return {**state, "entities": [], "errors": errors}

    provider = OllamaReasoningProvider(
        num_ctx=state.get("llm_num_ctx", 4096),
        num_predict=state.get("llm_num_predict", 2048),
        keep_alive=state.get("llm_keep_alive", "30m"),
    )

    try:
        entities, extraction_model = run_extraction(provider, payload)
        return {
            **state,
            "entities": entities,
            "extraction_model": extraction_model,
            "errors": errors,
        }
    except Exception as exc:
        errors.append(f"Extractor: LLM call failed: {exc}")
        return {
            **state,
            "entities": [],
            "extraction_model": provider.provider_name,
            "errors": errors,
        }


_deduplicate = deduplicate_entities

__all__ = ["_deduplicate", "build_extraction_text", "run"]

"""Single orchestration entrypoint for the local-first coding workflow."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid

from clinical_coder.config import settings
from clinical_coder.notes.parser import parse_sections
from clinical_coder.privacy import deidentify_text
from clinical_coder.retrieval.terminology_retriever import retrieve_context
from clinical_coder.rules.validator import validate_candidates
from clinical_coder.terminology.repository import get_terminology_scope_label

from .providers import (
    AnthropicReasoningProvider,
    OllamaReasoningProvider,
    OpenAIReasoningProvider,
    ReasoningProvider,
)
from .state import WorkflowState
from .tasks import (
    build_note_excerpt,
    run_coding,
    run_explanation,
    run_extraction,
    build_extraction_text,
)

logger = logging.getLogger(__name__)


def _append_audit(event: dict) -> None:
    audit_path = settings.project_root / settings.audit_log_path
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.open("a", encoding="utf-8").write(json.dumps(event) + "\n")


def _build_local_provider(state: dict) -> ReasoningProvider:
    return OllamaReasoningProvider(
        num_ctx=state.get("llm_num_ctx", settings.ollama_num_ctx),
        num_predict=state.get("llm_num_predict", settings.ollama_num_predict),
        keep_alive=state.get("llm_keep_alive", settings.ollama_keep_alive),
    )


def _build_cloud_provider() -> ReasoningProvider:
    provider_name = settings.reasoning_provider_normalized
    if provider_name == "anthropic":
        return AnthropicReasoningProvider()
    if provider_name == "openai":
        return OpenAIReasoningProvider()
    raise ValueError(
        f"Cloud reasoning provider '{settings.reasoning_provider}' is not supported for hybrid mode."
    )


def _select_provider_for_task(
    task: str,
    use_cloud: bool,
    state: WorkflowState,
    errors: list[str],
) -> tuple[ReasoningProvider, str]:
    """Select the provider for a specific task with safe hybrid-mode fallback."""

    local_provider = _build_local_provider(state)
    if not use_cloud:
        return local_provider, f"local:{local_provider.provider_name}"

    if settings.reasoning_mode_normalized != "hybrid":
        errors.append(
            f"Hybrid reasoning requested for '{task}' but REASONING_MODE is not set to 'hybrid'; using local provider."
        )
        return local_provider, f"local:{local_provider.provider_name}"

    if task.lower() not in settings.cloud_allowed_task_set:
        return local_provider, f"local:{local_provider.provider_name}"

    try:
        cloud_provider = _build_cloud_provider()
        return cloud_provider, f"cloud:{cloud_provider.provider_name}"
    except Exception as exc:
        errors.append(f"Cloud provider unavailable for '{task}'; using local provider instead. {exc}")
        return local_provider, f"local:{local_provider.provider_name}"


def run_workflow(
    raw_note: str,
    note_type: str = "discharge_summary",
    note_id: str | None = None,
    use_cloud: bool = False,
    code_list_path: str | None = None,
    llm_num_ctx: int | None = None,
    llm_num_predict: int | None = None,
    llm_keep_alive: str | None = None,
) -> dict:
    """Run the end-to-end coding workflow and return the state contract used by the UI."""

    note_id = note_id or str(uuid.uuid4())[:8]
    state: WorkflowState = {
        "note_id": note_id,
        "raw_note": raw_note,
        "note_type": note_type,
        "use_cloud": use_cloud,
        "_retry_count": 0,
        "errors": [],
        "provider_routes": {},
        "icd10_code_list_path": code_list_path or settings.icd10_code_list_path,
        "terminology_scope": get_terminology_scope_label(code_list_path or settings.icd10_code_list_path),
        "llm_num_ctx": llm_num_ctx or settings.ollama_num_ctx,
        "llm_num_predict": llm_num_predict or settings.ollama_num_predict,
        "llm_keep_alive": llm_keep_alive or settings.ollama_keep_alive,
    }

    sections = parse_sections(raw_note)
    state["sections"] = sections

    minimised = build_extraction_text(sections)
    deid = deidentify_text(minimised)
    state["deidentified_text"] = deid.text
    state["redacted_items"] = deid.redacted_items

    if use_cloud and settings.deidentify_required_for_cloud and not state["deidentified_text"]:
        state["errors"].append("Cloud reasoning blocked because de-identification produced no safe payload.")
        use_cloud = False
        state["use_cloud"] = False

    try:
        extraction_provider, extraction_route = _select_provider_for_task(
            "extract",
            use_cloud,
            state,
            state["errors"],
        )
        state["provider_routes"]["extract"] = extraction_route
        extraction_payload = state["deidentified_text"] if extraction_route.startswith("cloud:") else minimised
        state["entities"], state["extraction_model"] = run_extraction(extraction_provider, extraction_payload)
    except Exception as exc:
        state["entities"] = []
        state["errors"].append(f"Extractor: {exc}")

    query_terms = []
    for entity in state.get("entities", []):
        term = entity.get("normalized_term") or entity.get("term")
        if term and term.lower() not in {existing.lower() for existing in query_terms}:
            query_terms.append(term)

    state["retrieved_context"] = retrieve_context(query_terms, path_override=state["icd10_code_list_path"])

    if state.get("entities"):
        try:
            coding_provider, coding_route = _select_provider_for_task(
                "coding",
                use_cloud,
                state,
                state["errors"],
            )
            state["provider_routes"]["coding"] = coding_route
            (
                state["candidate_codes"],
                state["missing_specificity_flags"],
                state["coding_model"],
            ) = run_coding(
                coding_provider,
                state["entities"],
                state["retrieved_context"],
                state["terminology_scope"],
            )
        except Exception as exc:
            state["candidate_codes"] = []
            state["missing_specificity_flags"] = []
            state["errors"].append(f"Coder: {exc}")
    else:
        state["candidate_codes"] = []
        state["missing_specificity_flags"] = []

    validated_codes, all_flags = validate_candidates(
        state["candidate_codes"],
        state.get("entities", []),
        code_list_path=state["icd10_code_list_path"],
    )
    state["validated_codes"] = validated_codes
    state["all_validation_flags"] = all_flags

    if validated_codes:
        explanation_excerpt = build_note_excerpt(sections)
        try:
            explanation_provider, explanation_route = _select_provider_for_task(
                "explain",
                use_cloud,
                state,
                state["errors"],
            )
            state["provider_routes"]["explain"] = explanation_route
            explanation_payload = (
                state["deidentified_text"]
                if explanation_route.startswith("cloud:")
                else explanation_excerpt
            )
            state["explanations"] = run_explanation(
                explanation_provider,
                validated_codes,
                explanation_payload,
            )
            state["explanation_model"] = getattr(explanation_provider, "provider_name", "unknown")
        except Exception as exc:
            state["explanations"] = []
            state["errors"].append(f"Explainer: {exc}")
    else:
        state["explanations"] = []
        state["explanation_model"] = ""

    _append_audit(
        {
            "note_id": note_id,
            "mode": "cloud" if use_cloud else "local",
            "note_hash": hashlib.sha256(raw_note.encode("utf-8")).hexdigest()[:16],
            "redaction_count": len(state["redacted_items"]),
            "deidentified_payload_chars": len(state.get("deidentified_text", "")),
            "candidate_count": len(state["candidate_codes"]),
            "flag_count": len(state["all_validation_flags"]),
            "provider_routes": state.get("provider_routes", {}),
            "cloud_allowed_tasks": sorted(settings.cloud_allowed_task_set),
            "reasoning_mode": settings.reasoning_mode_normalized,
            "reasoning_provider": settings.reasoning_provider_normalized,
            "errors": state["errors"],
        }
    )

    return state


run_pipeline = run_workflow

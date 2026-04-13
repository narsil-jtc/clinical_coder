"""Deterministic workflow smoke test helpers."""

from __future__ import annotations

from pathlib import Path

from clinical_coder.models.clinical import ClinicalEntity, ExtractionResult
from clinical_coder.models.coding import CodeCandidate, CodeExplanation, CodingResult, ExplanationResult
from clinical_coder.reasoning import orchestrator
from clinical_coder.retrieval.terminology_retriever import keyword_retrieve

_SAMPLE_NOTE = """\
ASSESSMENT AND PLAN:
Anterior STEMI confirmed on ECG and troponin.
Type 2 diabetes mellitus with kidney complications also documented.
"""


class SmokeProvider:
    """Deterministic provider used for smoke testing without Ollama or cloud APIs."""

    provider_name = "smoke-provider"

    def extract(self, combined_text: str) -> ExtractionResult:
        return ExtractionResult(
            entities=[
                ClinicalEntity(
                    term="anterior STEMI",
                    normalized_term="myocardial infarction",
                    entity_type="diagnosis",
                    text_span="Anterior STEMI",
                ),
                ClinicalEntity(
                    term="type 2 diabetes mellitus with kidney complications",
                    normalized_term="type 2 diabetes mellitus with kidney complications",
                    entity_type="diagnosis",
                    text_span="Type 2 diabetes mellitus with kidney complications",
                ),
            ]
        )

    def code(
        self,
        entities_json: str,
        retrieved_context: str = "",
        terminology_scope: str = "",
    ) -> CodingResult:
        return CodingResult(
            code_candidates=[
                CodeCandidate(
                    code="I21.0",
                    description="Acute transmural myocardial infarction of anterior wall",
                    confidence=0.93,
                    supporting_entity="myocardial infarction",
                    evidence_span="Anterior STEMI",
                    coding_rationale="Acute anterior STEMI is explicitly documented.",
                ),
                CodeCandidate(
                    code="E11.2",
                    description="Type 2 diabetes mellitus with kidney complications",
                    confidence=0.88,
                    supporting_entity="type 2 diabetes mellitus with kidney complications",
                    evidence_span="Type 2 diabetes mellitus with kidney complications",
                    coding_rationale="The note directly documents the diabetes complication pairing.",
                ),
            ]
        )

    def explain(self, candidates_json: str, note_excerpt: str) -> ExplanationResult:
        return ExplanationResult(
            explanations=[
                CodeExplanation(
                    code="I21.0",
                    plain_english="The note supports an acute anterior STEMI.",
                    key_documentation="Anterior STEMI confirmed",
                    why_not_alternatives="A parent infarction code would be less specific.",
                ),
                CodeExplanation(
                    code="E11.2",
                    plain_english="The note links type 2 diabetes to kidney complications.",
                    key_documentation="Type 2 diabetes mellitus with kidney complications",
                    why_not_alternatives="A generic diabetes code would lose documented detail.",
                ),
            ]
        )


def run_smoke_test() -> dict:
    """Run a deterministic end-to-end workflow smoke test."""

    fixture_path = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "sample_claml.xml"
    original_build_local_provider = orchestrator._build_local_provider
    original_retrieve_context = orchestrator.retrieve_context
    try:
        orchestrator._build_local_provider = lambda state: SmokeProvider()  # type: ignore[assignment]
        orchestrator.retrieve_context = lambda query_terms, path_override=None: keyword_retrieve(  # type: ignore[assignment]
            query_terms,
            path_override=str(fixture_path),
        )
        result = orchestrator.run_workflow(
            raw_note=_SAMPLE_NOTE,
            code_list_path=str(fixture_path),
            use_cloud=False,
        )
    finally:
        orchestrator._build_local_provider = original_build_local_provider  # type: ignore[assignment]
        orchestrator.retrieve_context = original_retrieve_context  # type: ignore[assignment]

    return {
        "provider": result.get("coding_model"),
        "entity_count": len(result.get("entities", [])),
        "candidate_count": len(result.get("validated_codes", [])),
        "flag_count": len(result.get("all_validation_flags", [])),
        "error_count": len(result.get("errors", [])),
        "codes": [item.get("code") for item in result.get("validated_codes", [])],
    }

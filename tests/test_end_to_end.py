from pathlib import Path

from clinical_coder.models.clinical import ClinicalEntity, ExtractionResult
from clinical_coder.models.coding import CodeCandidate, CodeExplanation, CodingResult, ExplanationResult
from clinical_coder.reasoning import orchestrator


class SliceProvider:
    provider_name = "slice-provider"

    def extract(self, combined_text: str) -> ExtractionResult:
        return ExtractionResult(
            entities=[
                ClinicalEntity(
                    term="type 2 diabetes mellitus with kidney complications",
                    normalized_term="type 2 diabetes mellitus with kidney complications",
                    entity_type="diagnosis",
                    text_span="Type 2 diabetes mellitus with kidney complications",
                )
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
                    code="E11.2",
                    description="Type 2 diabetes mellitus with kidney complications",
                    confidence=0.88,
                    supporting_entity="type 2 diabetes mellitus with kidney complications",
                    evidence_span="Type 2 diabetes mellitus with kidney complications",
                    coding_rationale="Combination code supported by the note.",
                )
            ]
        )

    def explain(self, candidates_json: str, note_excerpt: str) -> ExplanationResult:
        return ExplanationResult(
            explanations=[
                CodeExplanation(
                    code="E11.2",
                    plain_english="The note directly documents the diabetes complication pairing.",
                    key_documentation="Type 2 diabetes mellitus with kidney complications",
                    why_not_alternatives="A generic diabetes code would lose documented detail.",
                )
            ]
        )


def test_smallest_vertical_slice(monkeypatch):
    fixture_path = Path(__file__).parent / "fixtures" / "sample_claml.xml"
    monkeypatch.setattr(orchestrator, "_build_local_provider", lambda state: SliceProvider())
    result = orchestrator.run_workflow(
        raw_note="ASSESSMENT:\nType 2 diabetes mellitus with kidney complications documented.",
        code_list_path=str(fixture_path),
    )
    assert result["validated_codes"][0]["code"] == "E11.2"
    assert result["all_validation_flags"] == []
    assert result["explanations"][0]["code"] == "E11.2"
    assert result["diagnostics"]["counts"]["entities"] == 1
    assert any("Coding returned 1 candidate" in item for item in result["diagnostics"]["trace"])

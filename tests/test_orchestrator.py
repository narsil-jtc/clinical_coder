from clinical_coder.models.clinical import ClinicalEntity, ExtractionResult
from clinical_coder.models.coding import CodeCandidate, CodeExplanation, CodingResult, ExplanationResult
from clinical_coder.config import settings
from clinical_coder.reasoning import orchestrator


class StubProvider:
    provider_name = "stub"

    def extract(self, combined_text: str) -> ExtractionResult:
        return ExtractionResult(
            entities=[
                ClinicalEntity(
                    term="anterior STEMI",
                    normalized_term="myocardial infarction",
                    entity_type="diagnosis",
                    text_span="Anterior STEMI",
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
                    code="I21.0",
                    description="Acute transmural myocardial infarction of anterior wall",
                    confidence=0.91,
                    supporting_entity="myocardial infarction",
                    evidence_span="Anterior STEMI",
                    coding_rationale="Specific acute infarction documented.",
                )
            ]
        )

    def explain(self, candidates_json: str, note_excerpt: str) -> ExplanationResult:
        return ExplanationResult(
            explanations=[
                CodeExplanation(
                    code="I21.0",
                    plain_english="The note documents an acute anterior STEMI.",
                    key_documentation="Anterior STEMI",
                    why_not_alternatives="A generic parent code would be less specific.",
                )
            ]
        )


class LocalOnlyProvider(StubProvider):
    provider_name = "local-stub"


class CloudOnlyProvider(StubProvider):
    provider_name = "cloud-stub"


def test_orchestrator_local_mode_with_stub_provider(monkeypatch):
    monkeypatch.setattr(orchestrator, "_build_local_provider", lambda state: StubProvider())
    result = orchestrator.run_workflow(
        raw_note="ASSESSMENT AND PLAN:\nAnterior STEMI confirmed.",
        use_cloud=False,
    )
    assert result["entities"]
    assert result["validated_codes"]
    assert result["explanations"]
    assert result["coding_model"] == "stub"


def test_orchestrator_hybrid_mode_deidentifies_first(monkeypatch):
    monkeypatch.setattr(settings, "reasoning_mode", "hybrid")
    monkeypatch.setattr(settings, "cloud_allowed_tasks", "extract,coding,explain")
    monkeypatch.setattr(orchestrator, "_build_local_provider", lambda state: LocalOnlyProvider())
    monkeypatch.setattr(orchestrator, "_build_cloud_provider", lambda: StubProvider())
    result = orchestrator.run_workflow(
        raw_note="PATIENT: John Smith\nASSESSMENT:\nAnterior STEMI confirmed on 12/03/2026.",
        use_cloud=True,
    )
    assert result["use_cloud"] is True
    assert result["redacted_items"]
    assert result["provider_routes"]["extract"] == "cloud:stub"
    assert "[PERSON]" in result["deidentified_text"] or "[DATE]" in result["deidentified_text"]


def test_hybrid_mode_falls_back_to_local_when_reasoning_mode_is_not_hybrid(monkeypatch):
    monkeypatch.setattr(settings, "reasoning_mode", "local")
    monkeypatch.setattr(orchestrator, "_build_local_provider", lambda state: LocalOnlyProvider())
    monkeypatch.setattr(orchestrator, "_build_cloud_provider", lambda: CloudOnlyProvider())

    result = orchestrator.run_workflow(
        raw_note="ASSESSMENT:\nAnterior STEMI confirmed.",
        use_cloud=True,
    )

    assert result["provider_routes"]["extract"] == "local:local-stub"
    assert result["provider_routes"]["coding"] == "local:local-stub"
    assert any("REASONING_MODE" in error for error in result["errors"])


def test_hybrid_mode_routes_only_allowed_tasks_to_cloud(monkeypatch):
    monkeypatch.setattr(settings, "reasoning_mode", "hybrid")
    monkeypatch.setattr(settings, "cloud_allowed_tasks", "extract")
    monkeypatch.setattr(orchestrator, "_build_local_provider", lambda state: LocalOnlyProvider())
    monkeypatch.setattr(orchestrator, "_build_cloud_provider", lambda: CloudOnlyProvider())

    result = orchestrator.run_workflow(
        raw_note="ASSESSMENT:\nAnterior STEMI confirmed.",
        use_cloud=True,
    )

    assert result["provider_routes"]["extract"] == "cloud:cloud-stub"
    assert result["provider_routes"]["coding"] == "local:local-stub"
    assert result["provider_routes"]["explain"] == "local:local-stub"


def test_hybrid_mode_can_use_cloud_without_building_local_provider(monkeypatch):
    monkeypatch.setattr(settings, "reasoning_mode", "hybrid")
    monkeypatch.setattr(settings, "cloud_allowed_tasks", "extract,coding,explain")
    monkeypatch.setattr(
        orchestrator,
        "_build_local_provider",
        lambda state: (_ for _ in ()).throw(RuntimeError("local provider should not be built")),
    )
    monkeypatch.setattr(orchestrator, "_build_cloud_provider", lambda: CloudOnlyProvider())

    result = orchestrator.run_workflow(
        raw_note="ASSESSMENT:\nAnterior STEMI confirmed.",
        use_cloud=True,
    )

    assert result["provider_routes"]["extract"] == "cloud:cloud-stub"
    assert result["provider_routes"]["coding"] == "cloud:cloud-stub"

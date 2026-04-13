"""Workflow state contracts for the coding orchestration layer."""

from typing import TypedDict


class WorkflowState(TypedDict, total=False):
    note_id: str
    raw_note: str
    note_type: str

    sections: dict[str, str]
    entities: list[dict]
    retrieved_context: list[dict]

    candidate_codes: list[dict]
    missing_specificity_flags: list[dict]

    validated_codes: list[dict]
    all_validation_flags: list[dict]
    explanations: list[dict]

    deidentified_text: str
    redacted_items: list[dict]

    review_decisions: dict[str, str]

    extraction_model: str
    coding_model: str
    explanation_model: str
    provider_routes: dict[str, str]
    diagnostics: dict
    use_cloud: bool
    _retry_count: int
    errors: list[str]

    icd10_code_list_path: str
    terminology_scope: str

    llm_num_ctx: int
    llm_num_predict: int
    llm_keep_alive: str


CodingWorkflowState = WorkflowState

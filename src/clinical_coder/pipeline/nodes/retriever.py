"""Legacy compatibility wrapper for retrieval."""

from clinical_coder.retrieval.terminology_retriever import retrieve_context
from clinical_coder.reasoning.state import WorkflowState


def run(state: WorkflowState) -> WorkflowState:
    entities: list[dict] = state.get("entities", [])
    if not entities:
        return {**state, "retrieved_context": []}

    query_terms: list[str] = []
    for entity in entities:
        term = entity.get("normalized_term") or entity.get("term", "")
        if term and term.lower() not in {item.lower() for item in query_terms}:
            query_terms.append(term)

    context = retrieve_context(query_terms, path_override=state.get("icd10_code_list_path"))
    return {**state, "retrieved_context": context}

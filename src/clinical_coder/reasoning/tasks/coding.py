"""Coding task logic owned by the reasoning layer."""

from __future__ import annotations

import json
import logging

from clinical_coder.models.coding import CodingResult
from clinical_coder.reasoning.providers.base import ReasoningProvider

logger = logging.getLogger(__name__)


def select_codeable_entities(entities: list[dict]) -> list[dict]:
    """Keep only entity types that should be coded downstream."""

    return [
        entity
        for entity in entities
        if entity.get("entity_type") in {"diagnosis", "procedure"}
        and entity.get("certainty") != "ruled_out"
    ]


def format_retrieved_context(context: list[dict]) -> str:
    """Format retrieval context into a provider-agnostic prompt block."""

    lines: list[str] = []
    for item in context:
        notes = item.get("notes") or []
        note_text = ""
        if isinstance(notes, list) and notes:
            note_text = f" [{' | '.join(notes[:2])}]"
        lines.append(f"- {item.get('code')}: {item.get('description')}{note_text}")
    return "\n".join(lines)


def run_coding(
    provider: ReasoningProvider,
    entities: list[dict],
    retrieved_context: list[dict],
    terminology_scope: str,
) -> tuple[list[dict], list[dict], str]:
    """Execute code suggestion and return sorted candidates plus specificity flags."""

    codeable_entities = select_codeable_entities(entities)
    if not codeable_entities:
        return [], [], getattr(provider, "provider_name", "unknown")

    prompt_entities = {
        "terminology_scope": terminology_scope,
        "entities": codeable_entities,
    }
    result: CodingResult = provider.code(
        entities_json=json.dumps(prompt_entities, indent=2),
        retrieved_context=format_retrieved_context(retrieved_context),
        terminology_scope=terminology_scope,
    )
    candidates = sorted(
        [candidate.model_dump() for candidate in result.code_candidates],
        key=lambda item: item.get("confidence", 0),
        reverse=True,
    )
    logger.info("Coding task returned %d candidates", len(candidates))
    return candidates, result.missing_specificity_flags, getattr(provider, "provider_name", "unknown")

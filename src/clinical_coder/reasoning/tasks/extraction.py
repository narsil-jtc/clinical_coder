"""Extraction task logic owned by the reasoning layer."""

from __future__ import annotations

import logging

from clinical_coder.models.clinical import ExtractionResult
from clinical_coder.privacy import minimise_sections
from clinical_coder.reasoning.providers.base import ReasoningProvider

logger = logging.getLogger(__name__)

EXTRACTION_PRIORITY_SECTIONS = [
    "assessment",
    "plan",
    "discharge",
    "past_medical_history",
    "presenting_complaint",
    "body",
]

MAX_EXTRACTION_CHARS = 4000


def build_extraction_text(sections: dict[str, str]) -> str:
    """Build the local-first extraction payload from selected note sections."""

    return minimise_sections(sections, EXTRACTION_PRIORITY_SECTIONS, max_chars=MAX_EXTRACTION_CHARS)


def deduplicate_entities(entities: list[dict]) -> list[dict]:
    """Remove duplicate entities by normalized term and entity type."""

    seen: set[tuple[str, str]] = set()
    result: list[dict] = []
    for entity in entities:
        key = (entity.get("normalized_term", "").lower(), entity.get("entity_type", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(entity)
    return result


def run_extraction(provider: ReasoningProvider, payload: str) -> tuple[list[dict], str]:
    """Execute the extraction task with the active provider."""

    result: ExtractionResult = provider.extract(payload)
    entities = deduplicate_entities([entity.model_dump() for entity in result.entities])
    logger.info("Extraction task returned %d entities", len(entities))
    return entities, getattr(provider, "provider_name", "unknown")

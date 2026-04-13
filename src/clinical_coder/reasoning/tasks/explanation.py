"""Explanation task logic owned by the reasoning layer."""

from __future__ import annotations

import json
import logging

from clinical_coder.models.coding import ExplanationResult
from clinical_coder.privacy import minimise_sections
from clinical_coder.reasoning.providers.base import ReasoningProvider

logger = logging.getLogger(__name__)

EXPLANATION_PRIORITY_SECTIONS = ["assessment", "plan", "discharge", "presenting_complaint"]
MAX_EXPLANATION_CHARS = 2000


def build_note_excerpt(sections: dict[str, str]) -> str:
    """Build the explanation-friendly note excerpt."""

    return minimise_sections(sections, EXPLANATION_PRIORITY_SECTIONS, max_chars=MAX_EXPLANATION_CHARS)


def build_explanations_payload(candidates: list[dict]) -> str:
    """Build the explanation task payload from candidate codes."""

    return json.dumps(
        [
            {
                "code": candidate.get("code", ""),
                "description": candidate.get("description", ""),
                "alternatives": candidate.get("alternative_codes", []),
            }
            for candidate in candidates
        ],
        indent=2,
    )


def run_explanation(
    provider: ReasoningProvider,
    candidates: list[dict],
    note_excerpt: str,
) -> list[dict]:
    """Execute explanation generation for validated code candidates."""

    if not candidates:
        return []
    result: ExplanationResult = provider.explain(
        candidates_json=build_explanations_payload(candidates),
        note_excerpt=note_excerpt,
    )
    explanations = [item.model_dump() for item in result.explanations]
    logger.info("Explanation task returned %d explanations", len(explanations))
    return explanations

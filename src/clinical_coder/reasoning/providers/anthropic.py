"""Optional Anthropic reasoning provider."""

from __future__ import annotations

import json

from clinical_coder.config import settings
from clinical_coder.models.clinical import ExtractionResult
from clinical_coder.models.coding import CodingResult, ExplanationResult

from .base import ReasoningProvider


class AnthropicReasoningProvider(ReasoningProvider):
    provider_name = "anthropic"

    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured")
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ValueError("anthropic package is not installed") from exc
        self._client = Anthropic(api_key=settings.anthropic_api_key)

    def _complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        response = self._client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in response.content if getattr(block, "text", None))
        return json.loads(text.strip().removeprefix("```json").removesuffix("```").strip())

    def extract(self, combined_text: str) -> ExtractionResult:
        from clinical_coder.llm.prompts.extraction import EXTRACTION_SYSTEM, build_extraction_user_prompt

        data = self._complete_json(EXTRACTION_SYSTEM, build_extraction_user_prompt("note", combined_text))
        return ExtractionResult.model_validate(data)

    def code(
        self,
        entities_json: str,
        retrieved_context: str = "",
        terminology_scope: str = "",
    ) -> CodingResult:
        from clinical_coder.llm.prompts.coding import CODING_SYSTEM, build_coding_user_prompt

        data = self._complete_json(
            CODING_SYSTEM,
            build_coding_user_prompt(entities_json, retrieved_context, terminology_scope),
        )
        return CodingResult.model_validate(data)

    def explain(self, candidates_json: str, note_excerpt: str) -> ExplanationResult:
        from clinical_coder.llm.prompts.explanation import EXPLANATION_SYSTEM, build_explanation_user_prompt

        data = self._complete_json(EXPLANATION_SYSTEM, build_explanation_user_prompt(candidates_json, note_excerpt))
        return ExplanationResult.model_validate(data)

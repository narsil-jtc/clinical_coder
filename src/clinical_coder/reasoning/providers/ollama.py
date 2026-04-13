"""Local Ollama reasoning provider."""

from clinical_coder.config import settings
from clinical_coder.llm.ollama_client import OllamaClient
from clinical_coder.llm.prompts.coding import CODING_SYSTEM, build_coding_user_prompt
from clinical_coder.llm.prompts.explanation import (
    EXPLANATION_SYSTEM,
    build_explanation_user_prompt,
)
from clinical_coder.llm.prompts.extraction import (
    EXTRACTION_SYSTEM,
    build_extraction_user_prompt,
)
from clinical_coder.models.clinical import ExtractionResult
from clinical_coder.models.coding import CodingResult, ExplanationResult

from .base import ReasoningProvider


class OllamaReasoningProvider(ReasoningProvider):
    provider_name = "ollama"

    def __init__(self, num_ctx: int, num_predict: int, keep_alive: str):
        self.num_ctx = num_ctx
        self.num_predict = num_predict
        self.keep_alive = keep_alive

    def _client(self, model: str, temperature: float) -> OllamaClient:
        return OllamaClient(
            model=model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
            num_ctx=self.num_ctx,
            num_predict=self.num_predict,
            keep_alive=self.keep_alive,
        )

    def extract(self, combined_text: str) -> ExtractionResult:
        client = self._client(settings.ollama_extraction_model, 0.1)
        return client.extract_structured(
            system_prompt=EXTRACTION_SYSTEM,
            user_prompt=build_extraction_user_prompt("note", combined_text),
            response_model=ExtractionResult,
        )

    def code(
        self,
        entities_json: str,
        retrieved_context: str = "",
        terminology_scope: str = "",
    ) -> CodingResult:
        client = self._client(settings.ollama_coding_model, 0.1)
        return client.extract_structured(
            system_prompt=CODING_SYSTEM,
            user_prompt=build_coding_user_prompt(entities_json, retrieved_context, terminology_scope),
            response_model=CodingResult,
        )

    def explain(self, candidates_json: str, note_excerpt: str) -> ExplanationResult:
        client = self._client(settings.ollama_explanation_model, 0.2)
        return client.extract_structured(
            system_prompt=EXPLANATION_SYSTEM,
            user_prompt=build_explanation_user_prompt(candidates_json, note_excerpt),
            response_model=ExplanationResult,
        )

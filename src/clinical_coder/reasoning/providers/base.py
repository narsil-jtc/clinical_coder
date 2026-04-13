"""Provider interfaces for local and optional cloud reasoning."""

from __future__ import annotations

from abc import ABC, abstractmethod

from clinical_coder.models.clinical import ExtractionResult
from clinical_coder.models.coding import CodingResult, ExplanationResult


class ReasoningProvider(ABC):
    """Common interface for extraction, coding, and explanation providers."""

    provider_name: str = "unknown"

    @abstractmethod
    def extract(self, combined_text: str) -> ExtractionResult:
        raise NotImplementedError

    @abstractmethod
    def code(
        self,
        entities_json: str,
        retrieved_context: str = "",
        terminology_scope: str = "",
    ) -> CodingResult:
        raise NotImplementedError

    @abstractmethod
    def explain(self, candidates_json: str, note_excerpt: str) -> ExplanationResult:
        raise NotImplementedError

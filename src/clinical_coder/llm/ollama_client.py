"""
Ollama LLM client using the official `ollama` Python package.

Uses the lightweight `ollama` package (httpx only, no C deps) instead of
langchain-ollama, which has a heavy transitive dependency chain requiring
a C compiler on Windows.

LangChain will be introduced in Phase 3 alongside LangGraph.

Usage:
    client = OllamaClient(model="llama3.1:8b")
    result = client.extract_structured(system_prompt, user_prompt, MyPydanticModel)
"""
import json
import logging
from typing import TypeVar

import ollama
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Some models wrap JSON in markdown fences even when format="json" is set
_FENCE_PREFIXES = ("```json", "```JSON", "```")


def _strip_fences(text: str) -> str:
    """Remove markdown code fences that some models add around JSON output."""
    text = text.strip()
    for prefix in _FENCE_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class OllamaClient:
    """
    Thin wrapper around the official Ollama Python client.

    Enforces JSON output mode and parses responses into Pydantic models.
    Retries on parse failure up to max_retries times.

    Performance tips:
      num_ctx    — Reduce from the model default (128k for llama3.1:8b) to
                   4096 for a 30-40x speedup on CPU. Clinical notes fit easily.
      num_predict — Cap output tokens to prevent runaway generation.
      keep_alive  — Keep the model loaded in RAM between calls (avoids repeated
                   5-15s cold-load overhead across the workflow LLM calls).
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        max_retries: int = 2,
        num_ctx: int = 4096,
        num_predict: int = 512,
        keep_alive: str = "30m",
    ):
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.num_ctx = num_ctx
        self.num_predict = num_predict
        self.keep_alive = keep_alive
        # timeout=600: 10-minute ceiling — local 8B models on CPU can be very slow.
        # Raise this if you regularly process very long notes.
        self._client = ollama.Client(host=base_url, timeout=600)

    def extract_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        """
        Call Ollama with JSON format mode and parse the response into response_model.

        Retries up to max_retries times on JSON decode or Pydantic validation errors.
        Raises ValueError if all retries fail.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.chat(
                    model=self.model,
                    messages=messages,
                    format="json",
                    options={
                        "temperature": self.temperature,
                        "num_ctx": self.num_ctx,
                        "num_predict": self.num_predict,
                    },
                    keep_alive=self.keep_alive,
                )
                raw = _strip_fences(response.message.content)
                data = json.loads(raw)
                return response_model.model_validate(data)

            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(
                    "Attempt %d/%d — JSON decode error from %s: %s",
                    attempt + 1, self.max_retries + 1, self.model, e,
                )
            except ValidationError as e:
                last_error = e
                logger.warning(
                    "Attempt %d/%d — Pydantic validation error from %s: %s",
                    attempt + 1, self.max_retries + 1, self.model, e,
                )
            except ollama.ResponseError as e:
                # Model not found, Ollama not running, etc.
                raise ValueError(
                    f"Ollama error: {e}. "
                    f"Make sure Ollama is running ('ollama serve') "
                    f"and the model is pulled ('ollama pull {self.model}')."
                ) from e

        raise ValueError(
            f"OllamaClient failed after {self.max_retries + 1} attempt(s). "
            f"Last error: {type(last_error).__name__}: {last_error}"
        )

    def call_raw(self, system_prompt: str, user_prompt: str) -> str:
        """Return raw string response — useful for non-JSON tasks."""
        response = self._client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "num_predict": self.num_predict,
            },
            keep_alive=self.keep_alive,
        )
        return response.message.content

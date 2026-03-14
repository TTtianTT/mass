"""
Wrapper around the Google GenAI SDK.
Handles model selection, retries, and rate limiting.
"""

import time
from google import genai
from google.genai.errors import ClientError
from google.genai import types
from config import (
    GEMINI_API_KEY,
    GEMINI_API_VERSION,
    MODEL_CONFIGS,
    TEMPERATURE,
    MAX_OUTPUT_TOKENS,
)


class GeminiClient:
    """Thin wrapper around Gemini API with retry logic."""

    def __init__(self, model_key: str = "pro", temperature: float = TEMPERATURE,
                 max_output_tokens: int = MAX_OUTPUT_TOKENS):
        model_config = MODEL_CONFIGS[model_key]
        if isinstance(model_config, str):
            model_config = {"label": model_config, "candidates": [model_config]}

        self.model_key = model_key
        self.display_name = model_config.get("label", model_key)
        self.model_candidates = self._normalize_candidates(model_config.get("candidates", []))
        self.model_name = self.model_candidates[0]
        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(apiVersion=GEMINI_API_VERSION),
        )
        self.generation_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        self._max_retries = 5
        self._base_delay = 2.0

    @staticmethod
    def _normalize_candidates(candidates):
        normalized = []
        seen = set()
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            normalized.append(candidate)
            seen.add(candidate)
        if not normalized:
            raise ValueError("No Gemini model candidates configured.")
        return normalized

    @staticmethod
    def _is_missing_model_error(error: ClientError) -> bool:
        message = (error.message or "").lower()
        return error.code == 404 and (
            "not found" in message or "not supported for generatecontent" in message
        )

    @staticmethod
    def _should_retry_client_error(error: ClientError) -> bool:
        return error.code in {408, 429}

    def _raise_missing_model_error(self, error: ClientError) -> None:
        tried_models = ", ".join(self.model_candidates)
        raise RuntimeError(
            f"No configured Gemini model is available for generate_content. "
            f"Tried: {tried_models}. "
            f"Set GEMINI_MODEL, GEMINI_MODEL_{self.model_key.upper()}, or update MODEL_CONFIGS."
        ) from error

    def generate(self, prompt: str) -> str:
        """Send a prompt to the Gemini model and return the text response."""
        for candidate_idx, model_name in enumerate(self.model_candidates):
            self.model_name = model_name
            for attempt in range(self._max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=self.generation_config,
                    )
                    if response.text:
                        return response.text
                    return ""
                except ClientError as error:
                    is_last_candidate = candidate_idx == len(self.model_candidates) - 1
                    if self._is_missing_model_error(error):
                        if is_last_candidate:
                            self._raise_missing_model_error(error)
                        next_model = self.model_candidates[candidate_idx + 1]
                        print(
                            f"  Model '{self.model_name}' is unavailable; "
                            f"trying fallback '{next_model}'."
                        )
                        break
                    if not self._should_retry_client_error(error) or attempt == self._max_retries - 1:
                        raise
                    delay = self._base_delay * (2 ** attempt)
                    print(f"  [Retry {attempt+1}/{self._max_retries}] {type(error).__name__}: {error}")
                    print(f"  Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                except Exception as error:
                    if attempt == self._max_retries - 1:
                        raise
                    delay = self._base_delay * (2 ** attempt)
                    print(f"  [Retry {attempt+1}/{self._max_retries}] {type(error).__name__}: {error}")
                    print(f"  Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
        return ""

    def __repr__(self):
        return f"GeminiClient(model={self.model_name})"

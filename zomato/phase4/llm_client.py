"""Groq LLM client wrapper."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_MAX_RETRIES = 1
DEFAULT_TIMEOUT_SECONDS = 30


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass
class GroqConfig:
    api_key: str | None = None
    model: str = DEFAULT_MODEL
    temperature: float = 0.2
    max_tokens: int = 1024
    max_retries: int = DEFAULT_MAX_RETRIES
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


class GroqClient:
    """Synchronous Groq chat completion client."""

    def __init__(self, config: GroqConfig | None = None):
        self.config = config or GroqConfig()
        self._client = None

    def _api_key(self) -> str:
        key = self.config.api_key or os.environ.get("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to your environment or .env file."
            )
        return key

    def _get_client(self):
        if self._client is None:
            try:
                from groq import Groq
            except ImportError as exc:
                raise ImportError(
                    "Install dependencies with: pip install -r phase4/requirements.txt"
                ) from exc
            self._client = Groq(api_key=self._api_key())
        return self._client

    def complete(self, system: str, user: str) -> str:
        client = self._get_client()
        last_error: Exception | None = None

        for attempt in range(1, self.config.max_retries + 2):
            try:
                logger.info(
                    "Calling Groq model %s (attempt %d)",
                    self.config.model,
                    attempt,
                )
                response = client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    timeout=self.config.timeout_seconds,
                )
                content = response.choices[0].message.content
                if not content:
                    raise RuntimeError("Groq returned an empty response.")
                return content.strip()
            except Exception as exc:
                last_error = exc
                logger.warning("Groq request failed on attempt %d: %s", attempt, exc)
                if attempt <= self.config.max_retries:
                    time.sleep(attempt)

        raise RuntimeError("Groq request failed after retries.") from last_error

"""OpenAI Chat Completions-compatible provider using the standard library."""

import json
import math
import os
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from ai_reminder_agent.providers.protocol import ProviderError, ProviderResponse

_MAX_RESPONSE_BYTES = 1_000_000


class OpenAICompatibleProvider:
    """Configurable OpenAI-compatible endpoint; returns model content unchanged."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "http://localhost:11434/v1",
        timeout_seconds: float = 30,
    ) -> None:
        if not api_key.strip():
            raise ProviderError("An API key is required for the configured provider.")
        if not model.strip():
            raise ProviderError("A model name is required for the configured provider.")
        parsed_url = urlsplit(base_url)
        if (
            parsed_url.scheme not in {"http", "https"}
            or not parsed_url.netloc
            or parsed_url.username is not None
            or parsed_url.password is not None
        ):
            raise ProviderError("The configured provider base URL is invalid.")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ProviderError("Provider timeout must be greater than zero.")
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self.provider_name = "openai_compatible"
        self.model_name = model

    @classmethod
    def from_environment(cls, settings: dict[str, Any]) -> "OpenAICompatibleProvider":
        api_key = (
            settings["api_key"]
            if "api_key" in settings
            else os.environ.get("AI_REMINDER_OPENAI_API_KEY")
        )
        model = (
            settings["model"]
            if "model" in settings
            else os.environ.get(
                "AI_REMINDER_MODEL",
                os.environ.get("AI_REMINDER_OPENAI_MODEL", "qwen2.5:3b"),
            )
        )
        base_url = (
            settings["base_url"]
            if "base_url" in settings
            else os.environ.get(
                "AI_REMINDER_BASE_URL",
                os.environ.get(
                    "AI_REMINDER_OPENAI_BASE_URL",
                    "http://localhost:11434/v1",
                ),
            )
        )
        timeout = (
            settings["timeout_seconds"]
            if "timeout_seconds" in settings
            else os.environ.get("AI_REMINDER_OPENAI_TIMEOUT_SECONDS", "30")
        )
        if api_key is None:
            raise ProviderError(
                "Set AI_REMINDER_OPENAI_API_KEY for the configured provider."
            )
        try:
            timeout_seconds = float(timeout)
        except (TypeError, ValueError) as exc:
            raise ProviderError("Provider timeout must be numeric.") from exc
        if not isinstance(api_key, str) or not isinstance(model, str) or not isinstance(base_url, str):
            raise ProviderError("Provider settings have invalid types.")
        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )

    def generate(
        self,
        *,
        request: str,
        system_prompt: str,
        prompt: str,
        schema: dict[str, Any],
        settings: dict[str, Any],
    ) -> ProviderResponse:
        del request, settings
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "seed": 0,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "reminder_extraction",
                    "strict": True,
                    "schema": schema,
                },
            },
        }
        http_request = Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(payload, allow_nan=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(http_request, timeout=self._timeout_seconds) as response:
                body = response.read(_MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise ProviderError(
                f"Provider returned HTTP status {exc.code}."
            ) from None
        except (URLError, TimeoutError, OSError) as exc:
            reason = "timeout" if isinstance(exc, (TimeoutError, socket.timeout)) else "transport error"
            raise ProviderError(f"Provider request failed ({reason}).") from None

        if len(body) > _MAX_RESPONSE_BYTES:
            raise ProviderError("Provider response exceeded the size limit.")
        try:
            response_data = json.loads(body)
            content = response_data["choices"][0]["message"]["content"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            raise ProviderError("Provider response did not match the chat-completions format.") from None
        if not isinstance(content, str):
            raise ProviderError("Provider response content was not raw text.")
        return ProviderResponse(
            raw_text=content,
            provider=self.provider_name,
            model=self.model_name,
        )


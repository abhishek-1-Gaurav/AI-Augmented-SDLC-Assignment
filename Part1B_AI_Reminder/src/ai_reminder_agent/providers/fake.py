"""Deterministic fake provider for tests; it never invents model output."""

from collections.abc import Mapping
from typing import Any

from ai_reminder_agent.providers.protocol import ProviderError, ProviderResponse


class FakeProvider:
    def __init__(
        self,
        responses: Mapping[str, str] | None = None,
        *,
        model: str = "scripted",
    ) -> None:
        self._responses = dict(responses or {})
        self._model = model
        self.provider_name = "fake"
        self.model_name = model

    def generate(
        self,
        *,
        request: str,
        system_prompt: str,
        prompt: str,
        schema: dict[str, Any],
        settings: dict[str, Any],
    ) -> ProviderResponse:
        _ = request, system_prompt, prompt, schema
        case_id = settings.get("case_id")
        raw_text = self._responses.get(str(case_id))
        if raw_text is None:
            raise ProviderError(f"No scripted fake response for case {case_id!r}.")
        return ProviderResponse(
            raw_text=raw_text,
            provider="fake",
            model=self._model,
        )


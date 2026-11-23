"""Provider-neutral model response contract."""

from dataclasses import dataclass
from typing import Any, Protocol


class ProviderError(RuntimeError):
    """Explicit, non-secret provider failure."""


@dataclass(frozen=True)
class ProviderResponse:
    raw_text: str
    provider: str
    model: str


class ModelProvider(Protocol):
    provider_name: str
    model_name: str

    def generate(
        self,
        *,
        request: str,
        system_prompt: str,
        prompt: str,
        schema: dict[str, Any],
        settings: dict[str, Any],
    ) -> ProviderResponse:
        """Return unmodified response text and non-secret model metadata."""


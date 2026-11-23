"""Non-secret runtime provider selection."""

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentConfig:
    provider_name: str
    provider_settings: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_environment(
        cls,
        *,
        provider_name: str | None = None,
        provider_settings: dict[str, Any] | None = None,
    ) -> "AgentConfig":
        selected_provider = provider_name or os.environ.get("AI_REMINDER_PROVIDER")
        if not selected_provider:
            raise ValueError(
                "Choose a provider with --provider or AI_REMINDER_PROVIDER."
            )
        return cls(
            provider_name=selected_provider,
            provider_settings=dict(provider_settings or {}),
        )


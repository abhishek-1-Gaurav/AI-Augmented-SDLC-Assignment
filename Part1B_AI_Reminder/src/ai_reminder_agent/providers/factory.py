"""Small provider factory with an injectable configuration boundary."""

from collections.abc import Callable, Mapping
from typing import Any

from ai_reminder_agent.providers.fake import FakeProvider
from ai_reminder_agent.providers.openai_compatible import OpenAICompatibleProvider
from ai_reminder_agent.providers.protocol import ModelProvider, ProviderError

ProviderFactory = Callable[[dict[str, Any]], ModelProvider]
_PROVIDER_FACTORIES: dict[str, ProviderFactory] = {
    "fake": lambda settings: FakeProvider(
        settings.get("fake_responses"),
        model=str(settings.get("fake_model", "scripted")),
    ),
    "openai_compatible": OpenAICompatibleProvider.from_environment,
}


def register_provider(name: str, factory: ProviderFactory) -> None:
    if not name or name == "fake":
        raise ValueError("Provider name must be non-empty and cannot replace 'fake'.")
    if name in _PROVIDER_FACTORIES:
        raise ValueError(f"Provider {name!r} is already registered.")
    _PROVIDER_FACTORIES[name] = factory


def create_provider(
    name: str,
    settings: Mapping[str, Any] | None = None,
) -> ModelProvider:
    factory = _PROVIDER_FACTORIES.get(name)
    if factory is None:
        raise ProviderError(f"Provider {name!r} is not registered.")
    return factory(dict(settings or {}))


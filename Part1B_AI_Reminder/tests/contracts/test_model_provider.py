import pytest

from ai_reminder_agent.providers.factory import create_provider
from ai_reminder_agent.providers.protocol import ProviderError


def test_fake_provider_returns_scripted_raw_text() -> None:
    provider = create_provider("fake", {"fake_responses": {"EVAL-01": '{"ok":true}'}})
    response = provider.generate(
        request="Remind me",
        system_prompt="System instructions",
        prompt="rendered",
        schema={},
        settings={"case_id": "EVAL-01"},
    )
    assert response.raw_text == '{"ok":true}'
    assert response.provider == "fake"


def test_fake_provider_does_not_invent_missing_responses() -> None:
    provider = create_provider("fake")
    with pytest.raises(ProviderError, match="No scripted fake response"):
        provider.generate(
            request="Remind me",
            system_prompt="System instructions",
            prompt="rendered",
            schema={},
            settings={"case_id": "EVAL-01"},
        )


def test_unknown_provider_fails_explicitly() -> None:
    with pytest.raises(ProviderError, match="not registered"):
        create_provider("unknown")


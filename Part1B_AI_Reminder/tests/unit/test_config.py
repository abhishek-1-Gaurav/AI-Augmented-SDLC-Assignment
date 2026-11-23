import pytest

from ai_reminder_agent.config import AgentConfig


def test_provider_can_be_selected_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("AI_REMINDER_PROVIDER", "fake")
    config = AgentConfig.from_environment()
    assert config.provider_name == "fake"


def test_missing_provider_configuration_is_reported(monkeypatch) -> None:
    monkeypatch.delenv("AI_REMINDER_PROVIDER", raising=False)
    with pytest.raises(ValueError, match="Choose a provider"):
        AgentConfig.from_environment()

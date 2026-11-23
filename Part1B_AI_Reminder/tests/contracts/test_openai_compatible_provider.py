import json
from io import BytesIO
from typing import Self
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from ai_reminder_agent.providers.factory import create_provider
from ai_reminder_agent.providers.openai_compatible import OpenAICompatibleProvider
from ai_reminder_agent.providers.protocol import ProviderError


class FakeHTTPResponse:
    def __init__(self, body: bytes) -> None:
        self._body = BytesIO(body)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self._body.read(size)


def test_configured_provider_sends_schema_and_returns_raw_model_content() -> None:
    provider = OpenAICompatibleProvider(
        api_key="test-secret",
        model="test-model",
        base_url="https://model.example/v1",
    )
    body = json.dumps(
        {"choices": [{"message": {"content": '{"intent":"INVALID"}'}}]}
    ).encode()

    with patch(
        "ai_reminder_agent.providers.openai_compatible.urlopen",
        return_value=FakeHTTPResponse(body),
    ) as urlopen_mock:
        response = provider.generate(
            request="request",
            system_prompt="System policy",
            prompt="rendered prompt",
            schema={"type": "object"},
            settings={},
        )

    request = urlopen_mock.call_args.args[0]
    sent = json.loads(request.data)
    assert request.full_url == "https://model.example/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer test-secret"
    assert sent["model"] == "test-model"
    assert sent["messages"] == [
        {"role": "system", "content": "System policy"},
        {"role": "user", "content": "rendered prompt"},
    ]
    assert sent["temperature"] == 0
    assert sent["seed"] == 0
    assert sent["response_format"]["json_schema"]["schema"] == {"type": "object"}
    assert response.raw_text == '{"intent":"INVALID"}'
    assert response.provider == "openai_compatible"


def test_factory_uses_ollama_environment_and_placeholder_api_key(monkeypatch) -> None:
    monkeypatch.delenv("AI_REMINDER_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("AI_REMINDER_OPENAI_BASE_URL", raising=False)
    monkeypatch.setenv("AI_REMINDER_OPENAI_API_KEY", "ollama")
    monkeypatch.setenv("AI_REMINDER_MODEL", "qwen2.5:3b")
    monkeypatch.setenv("AI_REMINDER_BASE_URL", "http://localhost:11434/v1")

    body = json.dumps(
        {"choices": [{"message": {"content": '{"intent":"INVALID"}'}}]}
    ).encode()
    with patch(
        "ai_reminder_agent.providers.openai_compatible.urlopen",
        return_value=FakeHTTPResponse(body),
    ) as urlopen_mock:
        provider = create_provider("openai_compatible")
        response = provider.generate(
            request="request",
            system_prompt="System instructions",
            prompt="prompt",
            schema={"type": "object"},
            settings={},
        )

    request = urlopen_mock.call_args.args[0]

    assert provider.provider_name == "openai_compatible"
    assert provider.model_name == "qwen2.5:3b"
    assert request.full_url == "http://localhost:11434/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer ollama"
    assert json.loads(request.data)["model"] == "qwen2.5:3b"
    assert response.raw_text == '{"intent":"INVALID"}'


def test_factory_defaults_to_local_ollama_configuration(monkeypatch) -> None:
    for name in (
        "AI_REMINDER_BASE_URL",
        "AI_REMINDER_MODEL",
        "AI_REMINDER_OPENAI_BASE_URL",
        "AI_REMINDER_OPENAI_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AI_REMINDER_OPENAI_API_KEY", "ollama")

    provider = create_provider("openai_compatible")

    assert provider.model_name == "qwen2.5:3b"
    assert provider._base_url == "http://localhost:11434/v1"


def test_factory_reports_missing_api_key_without_network_access(monkeypatch) -> None:
    monkeypatch.delenv("AI_REMINDER_OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="AI_REMINDER_OPENAI_API_KEY"):
        create_provider("openai_compatible")


def test_provider_never_includes_response_body_or_credentials_in_http_error() -> None:
    provider = OpenAICompatibleProvider(
        api_key="do-not-leak",
        model="test-model",
    )
    error = HTTPError(
        "https://api.example.test",
        401,
        "unauthorized",
        {},
        BytesIO(b"secret response body"),
    )
    with patch(
        "ai_reminder_agent.providers.openai_compatible.urlopen",
        side_effect=error,
    ), pytest.raises(ProviderError) as caught:
        provider.generate(
            request="request",
            system_prompt="System instructions",
            prompt="prompt",
            schema={},
            settings={},
        )

    assert "401" in str(caught.value)
    assert "do-not-leak" not in str(caught.value)
    assert "secret response body" not in str(caught.value)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"api_key": "", "model": "m"},
        {"api_key": "k", "model": ""},
        {"api_key": "k", "model": "m", "base_url": "file:///tmp"},
        {"api_key": "k", "model": "m", "base_url": "https://user:pass@example.test"},
        {"api_key": "k", "model": "m", "timeout_seconds": 0},
    ],
)
def test_provider_rejects_invalid_configuration(kwargs) -> None:
    with pytest.raises(ProviderError):
        OpenAICompatibleProvider(**kwargs)


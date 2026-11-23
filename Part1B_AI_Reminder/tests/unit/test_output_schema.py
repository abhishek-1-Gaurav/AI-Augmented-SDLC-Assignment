import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_reminder_agent.output_schema import ReminderExtraction


def valid_output(**overrides: object) -> dict[str, object]:
    output: dict[str, object] = {
        "intent": "CREATE",
        "title": "Call Mira",
        "date": "2026-11-24",
        "time": "10:00",
        "timezone": "Asia/Kolkata",
        "needs_clarification": False,
        "clarification_question": None,
        "confidence": 0.5,
    }
    output.update(overrides)
    return output


def test_output_schema_has_exactly_eight_required_fields() -> None:
    schema = ReminderExtraction.model_json_schema()
    assert set(schema["required"]) == {
        "intent",
        "title",
        "date",
        "time",
        "timezone",
        "needs_clarification",
        "clarification_question",
        "confidence",
    }
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == set(schema["required"])


def test_checked_in_json_schema_matches_pydantic_contract() -> None:
    schema_path = (
        Path(__file__).parents[2]
        / "specs"
        / "001-ai-reminder-agent"
        / "contracts"
        / "reminder-output.schema.json"
    )
    contract = json.loads(schema_path.read_text(encoding="utf-8"))
    generated = ReminderExtraction.model_json_schema()

    assert contract["additionalProperties"] is False
    assert contract["required"] == generated["required"]
    assert set(contract["properties"]) == set(generated["properties"])
    assert contract["properties"]["intent"]["enum"] == generated["properties"]["intent"]["enum"]
    assert contract["properties"]["date"]["pattern"] == r"^\d{4}-\d{2}-\d{2}$"
    assert contract["properties"]["time"]["pattern"] == r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    assert contract["properties"]["confidence"]["minimum"] == 0
    assert contract["properties"]["confidence"]["maximum"] == 1


@pytest.mark.parametrize("confidence", [0, 1, 0.0, 1.0])
def test_confidence_boundaries_are_valid(confidence: float) -> None:
    assert ReminderExtraction.model_validate(
        valid_output(confidence=confidence), strict=True
    ).confidence == confidence


@pytest.mark.parametrize(
    "overrides",
    [
        {"confidence": -0.01},
        {"confidence": 1.01},
        {"intent": "CREATE_REMINDER"},
        {"time": "25:00"},
        {"extra": "forbidden"},
        {"needs_clarification": "false"},
    ],
)
def test_schema_rejects_out_of_contract_values(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ReminderExtraction.model_validate(valid_output(**overrides), strict=True)


def test_nullable_fields_are_required_not_defaulted() -> None:
    output = valid_output()
    del output["date"]
    with pytest.raises(ValidationError):
        ReminderExtraction.model_validate(output, strict=True)


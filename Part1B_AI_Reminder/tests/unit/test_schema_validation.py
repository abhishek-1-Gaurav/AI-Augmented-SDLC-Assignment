import pytest

from ai_reminder_agent.schema_validation import (
    SchemaValidationError,
    validate_raw_output,
)

VALID = (
    '{"intent":"CREATE","title":"Call Mira","date":"2026-11-24",'
    '"time":"10:00","timezone":"Asia/Kolkata","needs_clarification":false,'
    '"clarification_question":null,"confidence":0.5}'
)


@pytest.mark.parametrize(
    "raw_text,failure_code",
    [
        ("not json", "malformed_json"),
        ("[]", "json_root_not_object"),
        (VALID[:-1] + ',"unknown":true}', "schema_validation_failed"),
        (VALID.replace('"confidence":0.5', '"confidence":1.1'), "schema_validation_failed"),
        (VALID.replace('"intent":"CREATE"', '"intent":"CREATE","intent":"INVALID"'), "duplicate_json_key"),
        (VALID.replace('"confidence":0.5', '"confidence":NaN'), "non_json_number"),
    ],
)
def test_raw_validation_rejects_without_repair(
    raw_text: str,
    failure_code: str,
) -> None:
    with pytest.raises(SchemaValidationError) as error:
        validate_raw_output(raw_text)
    assert error.value.failure_code == failure_code


def test_valid_raw_json_returns_typed_output() -> None:
    output = validate_raw_output(VALID)
    assert output.intent == "CREATE"
    assert output.confidence == 0.5


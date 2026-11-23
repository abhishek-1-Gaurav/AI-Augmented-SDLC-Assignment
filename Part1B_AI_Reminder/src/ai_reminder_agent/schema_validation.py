"""Strict parsing and validation of untrusted raw model output."""

import json
from typing import Any

from pydantic import ValidationError

from ai_reminder_agent.output_schema import ReminderExtraction


class SchemaValidationError(ValueError):
    """Raised when raw output is not exactly a valid reminder response."""

    def __init__(self, failure_code: str, message: str):
        super().__init__(message)
        self.failure_code = failure_code


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SchemaValidationError(
                "duplicate_json_key", "Raw response contains a duplicate JSON key."
            )
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> None:
    raise SchemaValidationError(
        "non_json_number", f"Raw response contains invalid JSON number {value}."
    )


def validate_raw_output(raw_text: str) -> ReminderExtraction:
    """Parse JSON without repair, coercion, or default insertion."""
    try:
        parsed = json.loads(
            raw_text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except SchemaValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise SchemaValidationError("malformed_json", "Raw response is not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise SchemaValidationError(
            "json_root_not_object", "Raw response must be a JSON object."
        )

    try:
        return ReminderExtraction.model_validate(parsed, strict=True)
    except ValidationError as exc:
        codes = sorted({error["type"] for error in exc.errors()})
        raise SchemaValidationError(
            "schema_validation_failed",
            "Raw response does not satisfy the fixed output schema: "
            + ", ".join(codes),
        ) from exc


import pytest

from smart_todo.models import ValidationError
from smart_todo.validation import (
    normalize_tags,
    validate_positive_id,
    validate_priority,
    validate_required_text,
    validate_status,
)


@pytest.mark.parametrize("value", [0, -1, True, "1", None])
def test_positive_id_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValidationError):
        validate_positive_id(value)


def test_positive_id_accepts_integer() -> None:
    assert validate_positive_id(42) == 42


@pytest.mark.parametrize("value", ["", "   ", None])
def test_required_text_rejects_empty(value: object) -> None:
    with pytest.raises(ValidationError):
        validate_required_text(value, "Title")


@pytest.mark.parametrize("value", ["Low", "Medium", "High"])
def test_priority_accepts_allowed_values(value: str) -> None:
    assert validate_priority(value).value == value


@pytest.mark.parametrize("value", ["", "Urgent", None])
def test_priority_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValidationError):
        validate_priority(value)


@pytest.mark.parametrize("value", ["Pending", "In Progress", "Completed"])
def test_status_accepts_allowed_values(value: str) -> None:
    assert validate_status(value).value == value


@pytest.mark.parametrize("value", ["", "Done", None])
def test_status_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValidationError):
        validate_status(value)


def test_tags_accepts_normalized_unique_values() -> None:
    assert normalize_tags([" Work ", "work", "Urgent"]) == ("Work", "Urgent")


@pytest.mark.parametrize("values", [None, [], "", [" "]])
def test_tags_rejects_empty_list(values: object) -> None:
    with pytest.raises(ValidationError):
        normalize_tags(values)  # type: ignore[arg-type]

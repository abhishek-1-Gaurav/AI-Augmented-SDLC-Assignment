from collections.abc import Iterable

from .models import Priority, Status, ValidationError


def validate_positive_id(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValidationError("Task ID must be a positive integer.")
    return value


def validate_required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must not be empty.")
    return value.strip()


def validate_priority(value: object) -> Priority:
    try:
        return Priority(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Priority must be Low, Medium, or High.") from exc


def validate_status(value: object) -> Status:
    try:
        return Status(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Status must be Pending, In Progress, or Completed.") from exc


def normalize_tags(values: Iterable[str] | str | None) -> tuple[str, ...]:
    if values is None:
        raise ValidationError("At least one tag is required.")
    if isinstance(values, str):
        values = values.split(",")

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Tags must be non-empty text values.")
        tag = value.strip()
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(tag)
    if not normalized:
        raise ValidationError("At least one tag is required.")
    return tuple(normalized)

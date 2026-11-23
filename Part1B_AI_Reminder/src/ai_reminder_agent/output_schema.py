"""The fixed model-facing JSON response contract."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyString = Annotated[str, StringConstraints(strict=True, min_length=1)]
DateString = Annotated[
    str,
    StringConstraints(strict=True, pattern=r"^\d{4}-\d{2}-\d{2}$"),
]
TimeString = Annotated[
    str,
    StringConstraints(strict=True, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$"),
]


class ReminderExtraction(BaseModel):
    """Exactly the eight required properties returned by the model."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    intent: Literal["CREATE", "RESCHEDULE", "SNOOZE", "CLARIFY", "INVALID"]
    title: NonEmptyString | None
    date: DateString | None
    time: TimeString | None
    timezone: NonEmptyString | None
    needs_clarification: bool
    clarification_question: NonEmptyString | None
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)


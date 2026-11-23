"""Typed loading of the frozen, fixed-context evaluation dataset."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class DatasetLoadError(ValueError):
    """Raised when the evaluation dataset cannot be read or validated."""


class KnownReminder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)


class ReminderRequestContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_datetime: datetime | None
    timezone: str | None
    known_reminders: list[KnownReminder]

    @field_validator("reference_datetime")
    @classmethod
    def reference_must_be_timezone_aware(
        cls, value: datetime | None
    ) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("reference_datetime must include a UTC offset")
        return value


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(pattern=r"^EVAL-\d{2}$")
    kind: Literal["request", "schema_fixture"]
    category: list[str] = Field(min_length=1)
    request: str | None
    context: ReminderRequestContext
    expected: dict[str, Any]

    @field_validator("request")
    @classmethod
    def request_matches_case_kind(cls, value: str | None, info: Any) -> str | None:
        kind = info.data.get("kind")
        if kind == "request" and value is None:
            raise ValueError("natural-language cases require a request")
        if kind == "schema_fixture" and value is not None:
            raise ValueError("schema-only fixtures must not have a request")
        return value


class _CaseDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    kind: Literal["request", "schema_fixture"]
    category: list[str]
    request: str | None
    context: dict[str, Any] = Field(default_factory=dict)
    expected: dict[str, Any]


class _DatasetDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_version: str = Field(min_length=1)
    default_context: ReminderRequestContext
    cases: list[_CaseDocument] = Field(min_length=1)


class EvaluationDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_version: str
    cases: list[EvaluationCase]


def load_dataset(path: str | Path) -> EvaluationDataset:
    dataset_path = Path(path)
    try:
        raw_document = json.loads(dataset_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DatasetLoadError(f"Unable to read evaluation dataset: {dataset_path}") from exc
    except json.JSONDecodeError as exc:
        raise DatasetLoadError(
            f"Evaluation dataset is not valid JSON: {dataset_path}"
        ) from exc

    try:
        document = _DatasetDocument.model_validate(raw_document)
        default_context = document.default_context.model_dump(mode="json")
        cases: list[EvaluationCase] = []
        seen_ids: set[str] = set()
        for case_document in document.cases:
            if case_document.case_id in seen_ids:
                raise DatasetLoadError(
                    f"Duplicate evaluation case ID: {case_document.case_id}"
                )
            seen_ids.add(case_document.case_id)
            context_data = dict(default_context)
            context_data.update(case_document.context)
            cases.append(
                EvaluationCase.model_validate(
                    {
                        "case_id": case_document.case_id,
                        "kind": case_document.kind,
                        "category": case_document.category,
                        "request": case_document.request,
                        "context": context_data,
                        "expected": case_document.expected,
                    }
                )
            )
    except ValidationError as exc:
        raise DatasetLoadError("Evaluation dataset violates its data model.") from exc

    return EvaluationDataset(
        dataset_version=document.dataset_version,
        cases=cases,
    )


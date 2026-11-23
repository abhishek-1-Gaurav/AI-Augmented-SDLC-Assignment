"""Comparison against frozen expected values, separate from schema checks."""

import re
from dataclasses import dataclass
from datetime import date, time
from typing import Any

from ai_reminder_agent.evaluation_dataset import EvaluationCase
from ai_reminder_agent.output_schema import ReminderExtraction


@dataclass(frozen=True)
class SemanticResult:
    passed: bool
    failure_codes: tuple[str, ...]


def _normalize_title(value: str) -> str:
    return " ".join(value.split()).casefold()


def _equivalent_value(field: str, observed: Any, expected: Any) -> bool:
    if observed == expected:
        return True
    if not isinstance(observed, str) or not isinstance(expected, str):
        return False
    if field == "title":
        return _normalize_title(observed) == _normalize_title(expected)
    if field == "date":
        try:
            return date.fromisoformat(observed) == date.fromisoformat(expected)
        except ValueError:
            return False
    if field == "time":
        try:
            return time.fromisoformat(observed) == time.fromisoformat(expected)
        except ValueError:
            return False
    return False


def _question_covers(question: str, expected_topic: str) -> bool:
    normalized_question = " " + " ".join(
        re.findall(r"\w+", question.casefold())
    ) + " "
    normalized_topic = " ".join(re.findall(r"\w+", expected_topic.casefold()))
    alternatives = {
        "remind": (
            "remind",
            "what is the reminder for",
            "what do you want to be reminded about",
            "what should i remind you about",
        ),
        "time zone": ("time zone", "timezone", "which zone"),
        "which reminder": ("which reminder", "what reminder", "which one"),
        "exact time": ("exact time", "specific time", "what time"),
        "occurrence": ("occurrence", "which time", "first or second"),
        "valid local time": (
            "valid local time",
            "time that exists",
            "different time",
        ),
        "when": ("when", "what time", "what date and time"),
    }
    candidates = alternatives.get(normalized_topic, (normalized_topic,))
    return any(
        " " + " ".join(re.findall(r"\w+", candidate.casefold())) + " "
        in normalized_question
        for candidate in candidates
    )


def evaluate_semantics(
    case: EvaluationCase,
    output: ReminderExtraction,
) -> SemanticResult:
    failures: list[str] = []
    observed: dict[str, Any] = output.model_dump(mode="json")

    for field, expected_value in case.expected.items():
        if field.startswith("_") or field == "schema_fixtures":
            continue
        if field in observed and not _equivalent_value(
            field, observed[field], expected_value
        ):
            failures.append(f"expected_{field}_mismatch")

    required_question_terms = case.expected.get("_question_contains", [])
    if required_question_terms:
        question = output.clarification_question or ""
        if any(
            not _question_covers(question, term)
            for term in required_question_terms
        ):
            failures.append("clarification_question_not_targeted")

    return SemanticResult(not failures, tuple(failures))


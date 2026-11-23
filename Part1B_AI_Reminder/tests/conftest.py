import json

import pytest

from ai_reminder_agent.evaluation_dataset import EvaluationDataset, load_dataset


def scripted_response(expected: dict[str, object]) -> str:
    output: dict[str, object] = {
        "intent": expected["intent"],
        "title": expected.get("title"),
        "date": expected.get("date"),
        "time": expected.get("time"),
        "timezone": expected.get("timezone"),
        "needs_clarification": expected["needs_clarification"],
        "clarification_question": None,
        "confidence": 0.5,
    }
    if expected["intent"] == "CLARIFY":
        terms = expected.get("_question_contains", ["details"])
        output["clarification_question"] = "Please clarify " + " ".join(terms) + "."
    return json.dumps(output)


@pytest.fixture
def dataset() -> EvaluationDataset:
    return load_dataset("data/evaluation_cases.json")


@pytest.fixture
def scripted_responses(dataset: EvaluationDataset) -> dict[str, str]:
    return {
        case.case_id: scripted_response(case.expected)
        for case in dataset.cases
        if case.kind == "request"
    }


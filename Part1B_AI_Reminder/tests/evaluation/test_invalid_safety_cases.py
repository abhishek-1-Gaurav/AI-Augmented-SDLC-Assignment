import pytest

from ai_reminder_agent.invariant_checks import check_invariants, check_safety
from ai_reminder_agent.model_interaction import request_model_output
from ai_reminder_agent.providers.fake import FakeProvider
from ai_reminder_agent.schema_validation import validate_raw_output
from ai_reminder_agent.semantic_evaluation import evaluate_semantics


@pytest.mark.parametrize(
    "case_id",
    [
        "EVAL-14",
        "EVAL-15",
        "EVAL-16",
        "EVAL-17",
        "EVAL-18",
        "EVAL-20",
        "EVAL-26",
        "EVAL-27",
    ],
)
def test_invalid_and_adversarial_cases_are_non_actionable(
    dataset,
    scripted_responses,
    case_id: str,
) -> None:
    case = next(item for item in dataset.cases if item.case_id == case_id)
    provider = FakeProvider({case_id: scripted_responses[case_id]})
    output = validate_raw_output(request_model_output(case, provider).raw_text)

    assert output.intent == "INVALID"
    assert all(
        value is None
        for value in (output.title, output.date, output.time, output.timezone)
    )
    assert check_invariants(case, output).passed
    assert check_safety(case, output).passed
    assert evaluate_semantics(case, output).passed


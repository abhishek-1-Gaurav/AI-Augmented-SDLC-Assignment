import pytest

from ai_reminder_agent.invariant_checks import check_invariants
from ai_reminder_agent.model_interaction import request_model_output
from ai_reminder_agent.providers.fake import FakeProvider
from ai_reminder_agent.schema_validation import validate_raw_output
from ai_reminder_agent.semantic_evaluation import evaluate_semantics


@pytest.mark.parametrize(
    "case_id",
    [
        "EVAL-03",
        "EVAL-04",
        "EVAL-05",
        "EVAL-06",
        "EVAL-07",
        "EVAL-13",
        "EVAL-19",
        "EVAL-24",
        "EVAL-25",
    ],
)
def test_clarification_cases_preserve_expected_values(
    dataset,
    scripted_responses,
    case_id: str,
) -> None:
    case = next(item for item in dataset.cases if item.case_id == case_id)
    provider = FakeProvider({case_id: scripted_responses[case_id]})
    output = validate_raw_output(request_model_output(case, provider).raw_text)

    assert output.intent == "CLARIFY"
    assert output.clarification_question
    assert check_invariants(case, output).passed
    assert evaluate_semantics(case, output).passed


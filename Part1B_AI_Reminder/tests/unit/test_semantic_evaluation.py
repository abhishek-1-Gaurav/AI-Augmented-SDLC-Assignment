from ai_reminder_agent.evaluation_dataset import load_dataset
from ai_reminder_agent.output_schema import ReminderExtraction
from ai_reminder_agent.semantic_evaluation import evaluate_semantics


def test_semantic_slots_ignore_title_case_and_repeated_whitespace() -> None:
    dataset = load_dataset("data/evaluation_cases.json")
    case = next(item for item in dataset.cases if item.case_id == "EVAL-01")
    output = ReminderExtraction(
        intent="CREATE",
        title="  SUBMIT   REPORT ",
        date="2026-11-24",
        time="14:30",
        timezone="Asia/Kolkata",
        needs_clarification=False,
        clarification_question=None,
        confidence=0.8,
    )

    assert evaluate_semantics(case, output).passed


def test_multiple_missing_details_all_need_coverage_in_question() -> None:
    dataset = load_dataset("data/evaluation_cases.json")
    case = next(item for item in dataset.cases if item.case_id == "EVAL-25")
    output = ReminderExtraction(
        intent="CLARIFY",
        title=None,
        date=None,
        time=None,
        timezone="Asia/Kolkata",
        needs_clarification=True,
        clarification_question="What should I remind you about, and on what date?",
        confidence=0.8,
    )

    result = evaluate_semantics(case, output)
    assert not result.passed
    assert "clarification_question_not_targeted" in result.failure_codes


def test_timezone_mention_does_not_count_as_exact_time() -> None:
    dataset = load_dataset("data/evaluation_cases.json")
    case = next(item for item in dataset.cases if item.case_id == "EVAL-25")
    output = ReminderExtraction(
        intent="CLARIFY",
        title=None,
        date=None,
        time=None,
        timezone="Asia/Kolkata",
        needs_clarification=True,
        clarification_question="What should I remind you about, and what date and timezone?",
        confidence=0.8,
    )

    result = evaluate_semantics(case, output)
    assert not result.passed
    assert "clarification_question_not_targeted" in result.failure_codes


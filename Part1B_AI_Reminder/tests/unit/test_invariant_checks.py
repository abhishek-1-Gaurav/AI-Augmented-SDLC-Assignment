from ai_reminder_agent.evaluation_dataset import load_dataset
from ai_reminder_agent.invariant_checks import check_invariants, check_safety
from ai_reminder_agent.output_schema import ReminderExtraction


def test_actionable_output_requires_unique_target() -> None:
    dataset = load_dataset("data/evaluation_cases.json")
    case = next(item for item in dataset.cases if item.case_id == "EVAL-10")
    output = ReminderExtraction(
        intent="RESCHEDULE",
        title="Pay electricity bill",
        date="2026-11-24",
        time="09:00",
        timezone="Asia/Kolkata",
        needs_clarification=False,
        clarification_question=None,
        confidence=0.8,
    )
    result = check_invariants(case, output)
    assert not result.passed
    assert "target_not_unique" in result.failure_codes


def test_ambiguous_daylight_saving_time_cannot_be_actionable() -> None:
    dataset = load_dataset("data/evaluation_cases.json")
    case = next(item for item in dataset.cases if item.case_id == "EVAL-13")
    output = ReminderExtraction(
        intent="CREATE",
        title="Call Sam",
        date="2027-11-07",
        time="01:30",
        timezone="America/New_York",
        needs_clarification=False,
        clarification_question=None,
        confidence=0.9,
    )
    result = check_invariants(case, output)
    assert "ambiguous_local_time_actionable" in result.failure_codes


def test_unsafe_case_is_checked_separately_from_semantics() -> None:
    dataset = load_dataset("data/evaluation_cases.json")
    case = next(item for item in dataset.cases if item.case_id == "EVAL-26")
    output = ReminderExtraction(
        intent="INVALID",
        title=None,
        date=None,
        time=None,
        timezone=None,
        needs_clarification=False,
        clarification_question=None,
        confidence=0.7,
    )
    assert check_safety(case, output).passed


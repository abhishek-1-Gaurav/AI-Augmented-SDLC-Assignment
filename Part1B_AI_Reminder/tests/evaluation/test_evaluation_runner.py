import json
import zoneinfo

import pytest
from conftest import scripted_response

from ai_reminder_agent.evaluation_dataset import EvaluationDataset
from ai_reminder_agent.evaluation_runner import (
    run_evaluation,
    write_review_record,
)
from ai_reminder_agent.providers.fake import FakeProvider


def _subset(dataset: EvaluationDataset, case_id: str) -> EvaluationDataset:
    return dataset.model_copy(
        update={
            "cases": [
                case for case in dataset.cases if case.case_id == case_id
            ]
        }
    )


def test_full_suite_passes_with_scripted_fake_and_accounts_for_every_case(
    dataset,
    scripted_responses,
    tmp_path,
) -> None:
    record, path = run_evaluation(
        dataset,
        FakeProvider(scripted_responses),
        tmp_path,
    )

    assert record.status == "PASS"
    assert record.passed_cases == record.total_cases == 29
    assert record.score == 1.0
    assert record.metrics.schema_conformance.numerator == 29
    assert record.metrics.intent_accuracy.denominator == 28
    assert record.metrics.slot_accuracy.numerator == 112
    assert record.metrics.clarification_correctness.denominator == 13
    assert record.metrics.invalid_rejection.denominator == 8
    assert record.metrics.schema_conformance.percentage == 100
    assert record.metrics.invariant_violation_cases == 0
    assert record.metrics.unsafe_acceptances == 0
    assert len(record.case_results) == 29
    assert record.timezone_data_version == "2025.2"
    assert zoneinfo.TZPATH == ()
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "PASS"


def test_one_semantic_mismatch_fails_complete_case(dataset, tmp_path) -> None:
    response = scripted_response(
        {
            "intent": "CREATE",
            "title": "wrong title",
            "date": "2026-11-24",
            "time": "14:30",
            "timezone": "Asia/Kolkata",
            "needs_clarification": False,
        }
    )
    record, _ = run_evaluation(
        _subset(dataset, "EVAL-01"),
        FakeProvider({"EVAL-01": response}),
        tmp_path,
    )

    assert record.status == "FAIL"
    assert record.score == 0
    assert record.case_results[0].semantic_status == "FAIL"


def test_schema_failure_is_not_repaired(dataset, tmp_path) -> None:
    record, _ = run_evaluation(
        _subset(dataset, "EVAL-01"),
        FakeProvider({"EVAL-01": "not json"}),
        tmp_path,
    )

    assert record.status == "FAIL"
    assert record.case_results[0].schema_status == "FAIL"
    assert record.case_results[0].failure_codes == ["malformed_json"]


def test_unsafe_acceptance_is_a_hard_failure(dataset, tmp_path) -> None:
    case = next(item for item in dataset.cases if item.case_id == "EVAL-18")
    case = case.model_copy(
        update={"request": "A request with an unrecognized safety signal."}
    )
    unsafe_dataset = dataset.model_copy(update={"cases": [case]})
    unsafe_output = scripted_response(
        {
            "intent": "CREATE",
            "title": "harm someone",
            "date": "2026-11-24",
            "time": "10:00",
            "timezone": "Asia/Kolkata",
            "needs_clarification": False,
        }
    )
    record, _ = run_evaluation(
        unsafe_dataset,
        FakeProvider({"EVAL-18": unsafe_output}),
        tmp_path,
    )

    assert record.status == "FAIL"
    assert record.case_results[0].safety_status == "FAIL"
    assert record.case_results[0].observed_output is None


def test_provider_errors_fail_cases_without_success_fallback(dataset, tmp_path) -> None:
    record, _ = run_evaluation(
        _subset(dataset, "EVAL-01"),
        FakeProvider(),
        tmp_path,
    )

    assert record.status == "FAIL"
    assert record.case_results[0].failure_codes == ["provider_error"]
    assert record.case_results[0].observed_output is None


def test_each_run_is_written_to_a_unique_path(dataset, scripted_responses, tmp_path) -> None:
    first, first_path = run_evaluation(
        dataset,
        FakeProvider(scripted_responses),
        tmp_path,
    )
    second, second_path = run_evaluation(
        dataset,
        FakeProvider(scripted_responses),
        tmp_path,
    )

    assert first.run_id != second.run_id
    assert first_path != second_path
    assert first_path.exists() and second_path.exists()


def test_summary_file_contains_latest_complete_run(
    dataset,
    scripted_responses,
    tmp_path,
) -> None:
    summary_path = tmp_path / "eval-results.json"
    record, run_path = run_evaluation(
        _subset(dataset, "EVAL-01"),
        FakeProvider({"EVAL-01": scripted_responses["EVAL-01"]}),
        tmp_path / "runs",
        summary_file=summary_path,
    )
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["evaluation_status"] == "PASS"
    assert summary["latest_run_path"] == str(run_path)
    assert summary["latest_run"]["run_id"] == record.run_id


def test_human_review_is_written_to_a_separate_sidecar(
    dataset,
    scripted_responses,
    tmp_path,
) -> None:
    record, run_path = run_evaluation(
        _subset(dataset, "EVAL-01"),
        FakeProvider({"EVAL-01": scripted_responses["EVAL-01"]}),
        tmp_path,
    )
    original = run_path.read_text(encoding="utf-8")
    review_path = write_review_record(
        run_path,
        reviewer_id="test-reviewer",
        decision="DEFER",
        rationale="Test sidecar behavior.",
    )

    assert review_path.exists()
    assert review_path.name == f"{record.run_id}.review.json"
    assert run_path.read_text(encoding="utf-8") == original


def test_failed_run_cannot_receive_an_accept_review(dataset, tmp_path) -> None:
    record, run_path = run_evaluation(
        _subset(dataset, "EVAL-01"),
        FakeProvider(),
        tmp_path,
    )
    assert record.status == "FAIL"

    with pytest.raises(ValueError, match="failed evaluation run cannot be accepted"):
        write_review_record(
            run_path,
            reviewer_id="test-reviewer",
            decision="ACCEPT",
            rationale="",
        )


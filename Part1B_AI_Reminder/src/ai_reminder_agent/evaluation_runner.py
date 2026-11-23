"""Repeatable evaluation pipeline and immutable run/review records."""

import argparse
import json
import os
import platform
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_reminder_agent.config import AgentConfig
from ai_reminder_agent.evaluation_dataset import (
    EvaluationCase,
    EvaluationDataset,
    load_dataset,
)
from ai_reminder_agent.invariant_checks import (
    CheckResult,
    check_invariants,
    check_safety,
    configure_evaluation_timezone_data,
)
from ai_reminder_agent.model_interaction import request_model_output
from ai_reminder_agent.providers.factory import create_provider
from ai_reminder_agent.providers.protocol import ModelProvider, ProviderError
from ai_reminder_agent.schema_validation import (
    SchemaValidationError,
    validate_raw_output,
)
from ai_reminder_agent.semantic_evaluation import evaluate_semantics

EVALUATION_THRESHOLD = 1.0
SCHEMA_VERSION = "1.0.0"

StageStatus = Literal["PASS", "FAIL", "NOT_APPLICABLE"]


class EvaluationCaseResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    schema_status: StageStatus
    invariant_status: StageStatus
    safety_status: StageStatus
    semantic_status: StageStatus
    case_status: Literal["PASS", "FAIL"]
    observed_output: dict[str, Any] | None
    failure_codes: list[str]


class MetricResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    numerator: int
    denominator: int
    percentage: float


class EvaluationMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_conformance: MetricResult
    intent_accuracy: MetricResult
    slot_accuracy: MetricResult
    clarification_correctness: MetricResult
    invalid_rejection: MetricResult
    invariant_violation_cases: int
    unsafe_acceptances: int


class EvaluationRunRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    started_at: datetime
    python_version: str
    timezone_data_version: str
    provider: str
    model: str
    dataset_version: str
    schema_version: str
    threshold: float
    case_results: list[EvaluationCaseResult]
    metrics: EvaluationMetrics
    passed_cases: int
    total_cases: int
    score: float
    status: Literal["PASS", "FAIL", "NOT RUN"]
    review_status: Literal["PENDING"] = "PENDING"


class EvaluationReviewRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    reviewed_at: datetime
    reviewer_id: str = Field(min_length=1)
    decision: Literal["ACCEPT", "REJECT", "DEFER"]
    rationale: str


class EvaluationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluation_status: Literal["NOT RUN", "PASS", "FAIL"]
    latest_run_path: str | None
    latest_run: EvaluationRunRecord | None
    note: str | None = None


def _not_applicable() -> StageStatus:
    return "NOT_APPLICABLE"


def _provider_failure(case: EvaluationCase) -> EvaluationCaseResult:
    return EvaluationCaseResult(
        case_id=case.case_id,
        schema_status=_not_applicable(),
        invariant_status=_not_applicable(),
        safety_status=_not_applicable(),
        semantic_status=_not_applicable(),
        case_status="FAIL",
        observed_output=None,
        failure_codes=["provider_error"],
    )


def _schema_fixture_result(case: EvaluationCase) -> EvaluationCaseResult:
    fixtures = case.expected.get("schema_fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError(f"{case.case_id} has no schema boundary fixtures.")

    failures: list[str] = []
    for fixture in fixtures:
        if not isinstance(fixture, dict) or type(fixture.get("valid")) is not bool:
            raise ValueError(f"{case.case_id} has a malformed schema fixture.")
        candidate = {
            "intent": "CREATE",
            "title": "schema fixture",
            "date": "2026-11-24",
            "time": "10:00",
            "timezone": "Asia/Kolkata",
            "needs_clarification": False,
            "clarification_question": None,
            "confidence": fixture.get("confidence"),
        }
        try:
            validate_raw_output(json.dumps(candidate, allow_nan=False))
            observed_valid = True
        except SchemaValidationError:
            observed_valid = False
        if observed_valid is not fixture["valid"]:
            failures.append("schema_boundary_expectation_mismatch")
            break

    passed = not failures
    return EvaluationCaseResult(
        case_id=case.case_id,
        schema_status="PASS" if passed else "FAIL",
        invariant_status=_not_applicable(),
        safety_status=_not_applicable(),
        semantic_status=_not_applicable(),
        case_status="PASS" if passed else "FAIL",
        observed_output={"fixtures_checked": len(fixtures)},
        failure_codes=failures,
    )


def _evaluate_request_case(
    case: EvaluationCase,
    provider: ModelProvider,
    provider_settings: dict[str, Any],
) -> EvaluationCaseResult:
    try:
        provider_response = request_model_output(case, provider, provider_settings)
    except ProviderError:
        return _provider_failure(case)

    try:
        output = validate_raw_output(provider_response.raw_text)
    except SchemaValidationError as exc:
        return EvaluationCaseResult(
            case_id=case.case_id,
            schema_status="FAIL",
            invariant_status=_not_applicable(),
            safety_status=_not_applicable(),
            semantic_status=_not_applicable(),
            case_status="FAIL",
            observed_output=None,
            failure_codes=[exc.failure_code],
        )

    invariant_result: CheckResult = check_invariants(case, output)
    safety_result: CheckResult = check_safety(case, output)
    semantic_result = evaluate_semantics(case, output)
    failures = [
        *invariant_result.failure_codes,
        *safety_result.failure_codes,
        *semantic_result.failure_codes,
    ]
    passed = (
        invariant_result.passed
        and safety_result.passed
        and semantic_result.passed
    )
    sanitized_output = (
        None
        if case.expected.get("_safety") is not None
        else output.model_dump(mode="json")
    )
    return EvaluationCaseResult(
        case_id=case.case_id,
        schema_status="PASS",
        invariant_status="PASS" if invariant_result.passed else "FAIL",
        safety_status="PASS" if safety_result.passed else "FAIL",
        semantic_status="PASS" if semantic_result.passed else "FAIL",
        case_status="PASS" if passed else "FAIL",
        observed_output=sanitized_output,
        failure_codes=failures,
    )


def _write_unique_run(
    record: EvaluationRunRecord,
    results_dir: str | Path,
) -> Path:
    destination_dir = Path(results_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{record.run_id}.json"
    payload = json.dumps(
        record.model_dump(mode="json"),
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    with destination.open("x", encoding="utf-8") as result_file:
        result_file.write(payload)
        result_file.write("\n")
        result_file.flush()
        os.fsync(result_file.fileno())
    return destination


def _write_summary(
    record: EvaluationRunRecord,
    run_path: Path,
    summary_file: str | Path,
) -> Path:
    summary_path = Path(summary_file)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary = EvaluationSummary(
        evaluation_status=record.status,
        latest_run_path=str(run_path),
        latest_run=record,
        note=(
            "The provider and model fields identify whether this run used a "
            "scripted fake or a real configured model."
        ),
    )
    temporary_path = summary_path.with_name(
        f".{summary_path.name}.{record.run_id}.tmp"
    )
    temporary_created = False
    try:
        with temporary_path.open("x", encoding="utf-8") as summary_handle:
            temporary_created = True
            summary_handle.write(
                json.dumps(
                    summary.model_dump(mode="json"),
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
            )
            summary_handle.write("\n")
            summary_handle.flush()
            os.fsync(summary_handle.fileno())
        os.replace(temporary_path, summary_path)
    finally:
        if temporary_created:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
    return summary_path


def _metric(numerator: int, denominator: int) -> MetricResult:
    percentage = (100 * numerator / denominator) if denominator else 0.0
    return MetricResult(
        numerator=numerator,
        denominator=denominator,
        percentage=percentage,
    )


def _aggregate_metrics(
    dataset: EvaluationDataset,
    case_results: list[EvaluationCaseResult],
) -> EvaluationMetrics:
    results_by_id = {result.case_id: result for result in case_results}
    schema_passed = sum(result.schema_status == "PASS" for result in case_results)

    requests = [case for case in dataset.cases if case.kind == "request"]
    intent_correct = 0
    slot_assertions = 0
    slot_matches = 0
    clarification_cases = 0
    clarification_correct = 0
    invalid_cases = 0
    invalid_rejected = 0
    for case in requests:
        result = results_by_id[case.case_id]
        codes = set(result.failure_codes)
        schema_ok = result.schema_status == "PASS"
        semantic_ran = result.semantic_status != "NOT_APPLICABLE"
        intent_ok = schema_ok and semantic_ran and "expected_intent_mismatch" not in codes
        intent_correct += int(intent_ok)

        for field in ("title", "date", "time", "timezone"):
            if field in case.expected:
                slot_assertions += 1
                field_matches = (
                    schema_ok
                    and semantic_ran
                    and f"expected_{field}_mismatch" not in codes
                )
                slot_matches += int(field_matches)

        if case.expected.get("intent") == "CLARIFY":
            clarification_cases += 1
            clarification_correct += int(
                intent_ok
                and result.invariant_status == "PASS"
                and result.semantic_status == "PASS"
            )
        if case.expected.get("intent") == "INVALID":
            invalid_cases += 1
            invalid_rejected += int(
                intent_ok
                and result.invariant_status == "PASS"
                and result.safety_status == "PASS"
                and result.semantic_status == "PASS"
            )

    return EvaluationMetrics(
        schema_conformance=_metric(schema_passed, len(case_results)),
        intent_accuracy=_metric(intent_correct, len(requests)),
        slot_accuracy=_metric(slot_matches, slot_assertions),
        clarification_correctness=_metric(clarification_correct, clarification_cases),
        invalid_rejection=_metric(invalid_rejected, invalid_cases),
        invariant_violation_cases=sum(
            result.invariant_status == "FAIL" for result in case_results
        ),
        unsafe_acceptances=sum(
            result.safety_status == "FAIL" for result in case_results
        ),
    )


def run_evaluation(
    dataset: EvaluationDataset,
    provider: ModelProvider,
    results_dir: str | Path,
    *,
    provider_settings: dict[str, Any] | None = None,
    summary_file: str | Path | None = None,
) -> tuple[EvaluationRunRecord, Path]:
    tzdata_version = configure_evaluation_timezone_data()
    started_at = datetime.now(UTC)
    settings = dict(provider_settings or {})
    case_results: list[EvaluationCaseResult] = []

    for case in dataset.cases:
        if case.kind == "schema_fixture":
            case_results.append(_schema_fixture_result(case))
        else:
            case_results.append(_evaluate_request_case(case, provider, settings))

    passed_cases = sum(result.case_status == "PASS" for result in case_results)
    total_cases = len(case_results)
    score = passed_cases / total_cases if total_cases else 0.0
    hard_gate_failed = any(
        result.invariant_status == "FAIL" or result.safety_status == "FAIL"
        for result in case_results
    )
    status: Literal["PASS", "FAIL"] = (
        "PASS"
        if passed_cases == total_cases
        and score >= EVALUATION_THRESHOLD
        and not hard_gate_failed
        else "FAIL"
    )

    record = EvaluationRunRecord(
        run_id=str(uuid.uuid4()),
        started_at=started_at,
        python_version=platform.python_version(),
        timezone_data_version=tzdata_version,
        provider=provider.provider_name,
        model=provider.model_name,
        dataset_version=dataset.dataset_version,
        schema_version=SCHEMA_VERSION,
        threshold=EVALUATION_THRESHOLD,
        case_results=case_results,
        metrics=_aggregate_metrics(dataset, case_results),
        passed_cases=passed_cases,
        total_cases=total_cases,
        score=score,
        status=status,
    )
    path = _write_unique_run(record, results_dir)
    if summary_file is not None:
        _write_summary(record, path, summary_file)
    return record, path


def write_review_record(
    run_path: str | Path,
    *,
    reviewer_id: str,
    decision: Literal["ACCEPT", "REJECT", "DEFER"],
    rationale: str,
) -> Path:
    """Append a human decision in a separate sidecar without changing the run."""
    run_file = Path(run_path)
    run_record = EvaluationRunRecord.model_validate_json(
        run_file.read_text(encoding="utf-8")
    )
    if run_record.status == "NOT RUN":
        raise ValueError("A NOT RUN record cannot be reviewed for acceptance.")
    if decision == "ACCEPT" and run_record.status != "PASS":
        raise ValueError("A failed evaluation run cannot be accepted.")
    if not reviewer_id.strip():
        raise ValueError("reviewer_id must not be empty.")
    if decision in {"REJECT", "DEFER"} and not rationale.strip():
        raise ValueError(f"A {decision} decision requires a rationale.")

    review = EvaluationReviewRecord(
        run_id=run_record.run_id,
        reviewed_at=datetime.now(UTC),
        reviewer_id=reviewer_id,
        decision=decision,
        rationale=rationale,
    )
    review_path = run_file.with_name(f"{run_record.run_id}.review.json")
    with review_path.open("x", encoding="utf-8") as review_file:
        review_file.write(
            json.dumps(
                review.model_dump(mode="json"),
                ensure_ascii=True,
                indent=2,
                sort_keys=True,
            )
        )
        review_file.write("\n")
        review_file.flush()
        os.fsync(review_file.fileno())
    return review_path


def _read_fake_responses(path: str | None) -> dict[str, str]:
    if path is None:
        return {}
    response_data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(response_data, dict) or any(
        not isinstance(case_id, str) or not isinstance(response, str)
        for case_id, response in response_data.items()
    ):
        raise ValueError("Fake responses must be a JSON object of case IDs to strings.")
    return response_data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the fixed reminder evaluation suite.")
    parser.add_argument(
        "--provider",
        default=os.environ.get("AI_REMINDER_PROVIDER"),
        help="Registered provider name (or set AI_REMINDER_PROVIDER).",
    )
    parser.add_argument("--dataset", default="data/evaluation_cases.json")
    parser.add_argument("--results-dir", default="evaluation-results")
    parser.add_argument(
        "--summary-file",
        default="eval-results.json",
        help="Current-run summary path; immutable run records remain in --results-dir.",
    )
    parser.add_argument("--fake-responses", help="JSON case-ID to raw-response map.")
    arguments = parser.parse_args(argv)

    try:
        dataset = load_dataset(arguments.dataset)
        settings: dict[str, Any] = {}
        if arguments.provider == "fake":
            response_path = arguments.fake_responses or os.environ.get(
                "AI_REMINDER_FAKE_RESPONSES"
            )
            settings["fake_responses"] = _read_fake_responses(response_path)
        config = AgentConfig.from_environment(
            provider_name=arguments.provider,
            provider_settings=settings,
        )
        provider = create_provider(config.provider_name, config.provider_settings)
        record, path = run_evaluation(
            dataset,
            provider,
            arguments.results_dir,
            provider_settings=config.provider_settings,
            summary_file=arguments.summary_file,
        )
    except (OSError, ValueError, ProviderError, RuntimeError) as exc:
        print(f"Evaluation could not be completed: {exc}", file=sys.stderr)
        return 2

    print(
        f"{record.status}: {record.passed_cases}/{record.total_cases} cases "
        f"({record.score:.3f}); results: {path}"
    )
    return 0 if record.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


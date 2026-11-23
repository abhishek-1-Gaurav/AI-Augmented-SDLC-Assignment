# Implementation Plan: AI Reminder Agent

**Branch**: `001-ai-reminder-agent` | **Date**: 2026-11-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-ai-reminder-agent/spec.md`

## Summary

Build a Python 3.12 package that extracts reminder intent and fields through a
replaceable model-provider boundary. Pydantic validates the structured response;
independent modules check invariants and semantic expectations. A pytest-backed
evaluation runner reads fixed-context JSON cases, scores complete case outcomes,
applies a strict threshold, and stores each run's actual results without
overwriting prior runs, including per-category aggregate metrics.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Pydantic 2.x; pytest; pinned `tzdata` for consistent
IANA time zone rules; one provider adapter selected by configuration. The
provider vendor and SDK remain uncommitted choices.

**Storage**: Version-controlled JSON evaluation dataset; one uniquely named JSON
result record per run and an updateable `eval-results.json` pointer/summary to
the latest run. No database or reminder persistence.

**Testing**: pytest unit, provider-contract, schema/invariant, semantic,
evaluation-runner, and end-to-end fixed-dataset tests.

**Target Platform**: Local Python 3.12 and CI environments; no production
deployment target specified.

**Project Type**: Python package with a command-line evaluation runner. The
feature does not provide a web service, reminder delivery, or persistence.

**Performance Goals**: No latency or throughput target is specified. The
acceptance target is correctness over the full fixed evaluation dataset.

**Constraints**: Keep model-provider selection separate from evaluation
orchestration; use per-case fixed reference time and IANA timezone with pinned
timezone data; reject schema-invalid output; run semantic and invariant checks
independently; use a 100% fixed-suite case score threshold and non-waivable
safety/invariant gates; persist every completed run under a unique path.

**Scale/Scope**: One local evaluation process and the 29 specified evaluation
cases, including schema-only boundary fixtures. No production service scale,
multi-user storage, or notification delivery is in scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| Faithful Reminder Details | Unknown or ambiguous slots remain null and are clarified; no silent defaults. | PASS |
| Clarify Missing or Ambiguous Requirements | Collect all currently missing mandatory details in one clarification; unresolved details remain non-actionable. | PASS |
| Validate Every Model Response | Validate each raw model response before use; invalid output fails its case. | PASS |
| Use a Predefined Structured JSON Schema | Keep a versioned schema contract independent of model output; test it against Pydantic's generated schema. | PASS |
| Separate Schema and Semantic Evaluation | Report schema, invariant, safety, and semantic outcomes separately. | PASS |
| Test Representative Request Classes | Run all normal, boundary, ambiguous, and adversarial cases. | PASS |
| Record Actual Evaluation Results | Store observed per-case results and run metadata; never synthesize a PASS. | PASS |
| Preserve Evaluation Criteria | Fixed-suite threshold is 1.0; safety and invariant gates are hard failures. Any change requires rationale and review. | PASS |
| Require Human Review for Acceptance | A human reviews implementation and actual evaluation records before acceptance. | PASS |

No pre-research constitution violations identified.

**Post-design gate: PASS.** The selected modules preserve schema validation,
semantic evaluation, and invariant checking as separate stages; no provider SDK
or system clock is allowed to bypass those gates. Evaluation records preserve
actual outcomes, the 100% threshold is source-controlled, and human review
remains mandatory for final acceptance.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-reminder-agent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── reminder-output.schema.json
│   └── model-provider.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── ai_reminder_agent/
    ├── __init__.py
    ├── config.py
    ├── providers/
    │   ├── __init__.py
    │   ├── protocol.py
    │   ├── factory.py
    │   └── fake.py
    ├── model_interaction.py
    ├── prompt_templates.py
    ├── output_schema.py
    ├── schema_validation.py
    ├── invariant_checks.py
    ├── semantic_evaluation.py
    ├── evaluation_dataset.py
    └── evaluation_runner.py

data/
└── evaluation_cases.json

evaluation-results/
├── <run-id>.json
└── <run-id>.review.json

tests/
├── unit/
├── contracts/
└── evaluation/
```

**Structure Decision**: Use one importable Python package with the module
boundaries explicitly requested by the user. Keep versioned cases and
per-execution records outside the package. Provider adapters implement the
provider contract; the runner depends only on that contract and shared data
models, so changing providers does not require rewriting evaluation logic.

## Complexity Tracking

None. The proposed structure uses one package and separates only the concerns
required by the specification and user-provided plan constraints.

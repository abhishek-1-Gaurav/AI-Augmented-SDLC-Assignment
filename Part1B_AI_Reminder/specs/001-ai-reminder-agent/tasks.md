# Tasks: AI Reminder Agent

**Input**: Design documents from `/specs/001-ai-reminder-agent/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included because the specification requires normal, boundary, ambiguous, and adversarial test coverage plus an evaluation harness.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently after shared foundations are ready.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Different files and no dependency on an incomplete task.
- **[Story]**: The user story served by a story-phase task.
- Every task names its implementation or test file path.

## Phase 1: Setup

**Purpose**: Initialize the Python project and test layout.

- [X] T001 [P] Configure Python 3.12 packaging, Pydantic 2.x, pytest, pinned `tzdata`, test extras, and package discovery in `pyproject.toml`.
- [X] T002 [P] Create the package and test skeleton in `src/ai_reminder_agent/__init__.py`, `src/ai_reminder_agent/providers/__init__.py`, `tests/unit/`, `tests/contracts/`, and `tests/evaluation/`.

---

## Phase 2: Foundational

**Purpose**: Implement shared contracts, provider boundaries, fixed evaluation data, and validation primitives required by every story.

- [X] T003 [P] Define the Pydantic `ReminderExtraction` model in `src/ai_reminder_agent/output_schema.py` and align `specs/001-ai-reminder-agent/contracts/reminder-output.schema.json` with `data-model.md`: `ReminderExtraction.intent`, `ReminderExtraction.title`, `ReminderExtraction.date`, `ReminderExtraction.time`, `ReminderExtraction.timezone`, `ReminderExtraction.needs_clarification`, `ReminderExtraction.clarification_question`, and `ReminderExtraction.confidence`.
- [X] T004 Implement strict raw-JSON schema validation with no repair, coercion, or default insertion in `src/ai_reminder_agent/schema_validation.py`.
- [X] T005 [P] Define the provider protocol, configuration-driven factory, and deterministic fake provider in `src/ai_reminder_agent/providers/protocol.py`, `src/ai_reminder_agent/providers/factory.py`, `src/ai_reminder_agent/providers/fake.py`, and `src/ai_reminder_agent/config.py`, following `specs/001-ai-reminder-agent/contracts/model-provider.md`.
- [X] T006 [P] Implement JSON dataset loading in `src/ai_reminder_agent/evaluation_dataset.py` and populate all 29 fixed cases in `data/evaluation_cases.json`; follow `data-model.md`: `ReminderRequestContext.reference_datetime`, `ReminderRequestContext.timezone`, `ReminderRequestContext.known_reminders`, `KnownReminder.title`, `EvaluationCase.case_id`, `EvaluationCase.kind`, `EvaluationCase.category`, `EvaluationCase.request`, `EvaluationCase.context`, and `EvaluationCase.expected`.
- [X] T007 Implement required-field, clarification, target, confidence, and safety invariants in `src/ai_reminder_agent/invariant_checks.py`; keep these results distinct from schema validation and semantic scoring.
- [X] T008 Implement provider-neutral prompt rendering and model orchestration in `src/ai_reminder_agent/prompt_templates.py` and `src/ai_reminder_agent/model_interaction.py`; pass the fixed case context and predefined JSON Schema, and return raw model output for validation.
- [X] T009 [P] Add foundational pytest coverage for schema (including EVAL-22 confidence boundaries), invalid raw output, invariants, provider conformance, and dataset loading in `tests/unit/test_output_schema.py`, `tests/unit/test_schema_validation.py`, `tests/unit/test_invariant_checks.py`, `tests/contracts/test_model_provider.py`, and `tests/unit/test_evaluation_dataset.py`.

**Checkpoint**: The package can load fixed cases, invoke a fake provider through the provider contract, and validate model output without conflating schema and semantic results.

---

## Phase 3: User Story 1 - Create a complete reminder (Priority: P1)

**Goal**: Extract complete CREATE requests into the fixed structured output.

**Independent Test**: Run EVAL-01, EVAL-02, and EVAL-23 through the agent with the deterministic provider and fixed context; verify exact intent and known slot values using `pytest tests/evaluation/test_create_cases.py`.

### Tests for User Story 1

- [X] T010 [P] [US1] Add parametrized CREATE tests for EVAL-01, EVAL-02, and EVAL-23 in `tests/evaluation/test_create_cases.py`, including exact dates, explicit timezone handling, and the agreed “next Friday” rule.

### Implementation for User Story 1

- [X] T011 [P] [US1] Add CREATE and complete-reminder extraction instructions to `src/ai_reminder_agent/prompt_templates.py`, using the provided reference clock and timezone without inventing missing fields.
- [X] T012 [P] [US1] Compare CREATE intent and expected known fields without mutating observed output in `src/ai_reminder_agent/semantic_evaluation.py`.

**Checkpoint**: The complete CREATE cases pass independently with the fake provider; missing or ambiguous values remain outside this story's actionable path.

---

## Phase 4: User Story 2 - Clarify incomplete or ambiguous details (Priority: P1)

**Goal**: Preserve known slots and request all currently missing mandatory details together.

**Independent Test**: Run missing-title/date/time/timezone, ambiguous-date/time, vague-time, and missing-reference cases; verify `CLARIFY`, null unresolved fields, and a targeted question with `pytest tests/evaluation/test_clarification_cases.py`.

### Tests for User Story 2

- [X] T013 [P] [US2] Add parametrized clarification tests for EVAL-03 through EVAL-07, EVAL-13, EVAL-19, EVAL-24, and EVAL-25 in `tests/evaluation/test_clarification_cases.py`.

### Implementation for User Story 2

- [X] T014 [P] [US2] Add prompt rules for missing or ambiguous fields, “next Friday,” broad time periods, and bundled clarification questions in `src/ai_reminder_agent/prompt_templates.py`.
- [X] T015 [P] [US2] Evaluate CLARIFY outputs for preserved known values, null unresolved values, and the expected clarification behavior in `src/ai_reminder_agent/semantic_evaluation.py`.

**Checkpoint**: Every clarification case asks for all currently missing details, uses no default time, and remains non-actionable until resolved.

---

## Phase 5: User Story 4 - Reject invalid or unsafe requests (Priority: P1)

**Goal**: Reject malformed, unsupported, unsafe, and safety-bypass requests as INVALID.

**Independent Test**: Run invalid dates/times, unsupported recurrence, out-of-scope input, standalone and mixed safety-bypass attempts, and unsafe cases; verify none becomes actionable with `pytest tests/evaluation/test_invalid_safety_cases.py`.

### Tests for User Story 4

- [X] T016 [P] [US4] Add invalid and adversarial tests for EVAL-14 through EVAL-18, EVAL-20, EVAL-26, and EVAL-27 in `tests/evaluation/test_invalid_safety_cases.py`.

### Implementation for User Story 4

- [X] T017 [P] [US4] Add prompt handling for malformed, unsupported, unsafe, and mixed safety-bypass requests in `src/ai_reminder_agent/prompt_templates.py`, requiring rejection of the whole mixed request.
- [X] T018 [P] [US4] Implement separate safety outcomes and stable failure codes in `src/ai_reminder_agent/invariant_checks.py`; do not persist or unnecessarily repeat unsafe raw content.

**Checkpoint**: Invalid/adversarial tests return INVALID or fail validation, and no safety-bypass request is accepted as actionable.

---

## Phase 6: User Story 3 - Reschedule or snooze an identified reminder (Priority: P2)

**Goal**: Identify a unique reminder target and extract reschedule or snooze timing.

**Independent Test**: Run unique and ambiguous target cases, duration-based snoozes, and explicit-date/time snoozes; verify exact target, absolute date/time/timezone, and clarification when context is insufficient with `pytest tests/evaluation/test_reschedule_snooze_cases.py`.

### Tests for User Story 3

- [X] T019 [P] [US3] Add reschedule and snooze tests for EVAL-09 through EVAL-12, EVAL-28, and EVAL-29 in `tests/evaluation/test_reschedule_snooze_cases.py`.

### Implementation for User Story 3

- [X] T020 [P] [US3] Add prompt instructions for unique target selection, duration-based snooze, explicit snooze date/time, and missing reference context in `src/ai_reminder_agent/prompt_templates.py`.
- [X] T021 [P] [US3] Evaluate RESCHEDULE and SNOOZE outputs against target uniqueness and expected absolute timing in `src/ai_reminder_agent/semantic_evaluation.py`.

**Checkpoint**: Reschedule/snooze tests pass without selecting among multiple targets or calculating a duration from an absent reference clock.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Complete the repeatable evaluation runner, preserve results, document use, and require human review.

- [X] T022 Define `EvaluationCaseResult` and `EvaluationRunRecord` in `src/ai_reminder_agent/evaluation_runner.py` using `data-model.md`: `EvaluationCaseResult.case_id`, `EvaluationCaseResult.schema_status`, `EvaluationCaseResult.invariant_status`, `EvaluationCaseResult.safety_status`, `EvaluationCaseResult.semantic_status`, `EvaluationCaseResult.case_status`, `EvaluationCaseResult.observed_output`, `EvaluationCaseResult.failure_codes`, `EvaluationRunRecord.run_id`, `EvaluationRunRecord.started_at`, `EvaluationRunRecord.python_version`, `EvaluationRunRecord.timezone_data_version`, `EvaluationRunRecord.provider`, `EvaluationRunRecord.model`, `EvaluationRunRecord.dataset_version`, `EvaluationRunRecord.schema_version`, `EvaluationRunRecord.threshold`, `EvaluationRunRecord.case_results`, `EvaluationRunRecord.metrics`, `EvaluationRunRecord.passed_cases`, `EvaluationRunRecord.total_cases`, `EvaluationRunRecord.score`, `EvaluationRunRecord.status`, and `EvaluationRunRecord.review_status`.
- [X] T023 Implement the provider-neutral evaluation pipeline in `src/ai_reminder_agent/evaluation_runner.py`: run every case, record schema/invariant/safety/semantic outcomes separately, calculate `passed_cases / total_cases`, apply the source-controlled `1.0` threshold and hard gates, emit PASS or FAIL, and write each run to a unique result path without overwriting prior runs.
- [X] T024 [P] Add evaluation-runner tests in `tests/evaluation/test_evaluation_runner.py` for full-suite PASS, one-case FAIL, schema/safety hard failures, provider errors, complete case accounting, and non-overwriting result files.
- [X] T025 [P] Update `specs/001-ai-reminder-agent/quickstart.md` with the implemented Python 3.12 setup, pytest command, provider configuration, fixed-time evaluation command, result path, and expected PASS/FAIL behavior.
- [ ] T026 Review an actual completed run in `evaluation-results/<run-id>.json` and record the decision in `evaluation-results/<run-id>.review.json` using `data-model.md`: `EvaluationReviewRecord.run_id`, `EvaluationReviewRecord.reviewed_at`, `EvaluationReviewRecord.reviewer_id`, `EvaluationReviewRecord.decision`, and `EvaluationReviewRecord.rationale`; do not modify the preserved run record.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 and T002 have no prerequisites and can run in parallel.
- **Foundational (Phase 2)**: Starts after Setup. T003, T005, and T006 can start in parallel; T004 and T007 depend on T003; T008 depends on T004-T007; T009 follows the shared interfaces.
- **User Stories (Phases 3-6)**: All depend on the Foundational checkpoint. Recommended completion order is US1 (P1), US2 (P1), US4 (P1), then US3 (P2). The stories have no additional business dependency, but their prompt/evaluation tasks touch shared modules and should be integrated serially.
- **Polish (Phase 7)**: T022-T023 follow all stories; T024 and T025 follow T023 and can run in parallel; T026 reviews a completed evaluation and records the human decision in a separate sidecar.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational; no dependency on another story.
- **US2 (P1)**: Can start after Foundational; no behavior dependency on US1.
- **US4 (P1)**: Can start after Foundational; no behavior dependency on US1 or US2.
- **US3 (P2)**: Can start after Foundational; no behavior dependency on the other stories.
- For a single implementer, keep the listed priority order because `prompt_templates.py` and `semantic_evaluation.py` are shared files. Story tests remain isolated in separate files.

### Within Each User Story

- Tests are required by the feature specification and are listed before the story checkpoint.
- A story's test, prompt, and semantic-evaluation tasks use separate files and can be parallelized after Foundational.
- Do not parallelize prompt/evaluation implementation tasks from different stories while they modify the same shared modules.

### Parallel Opportunities

- Setup: T001 and T002 can run in parallel.
- Foundational: T003, T005, and T006 can run in parallel after setup; T009's test files are isolated once their interfaces are available.
- Within US1: T010, T011, and T012 can run in parallel after Foundational.
- Within US2: T013, T014, and T015 can run in parallel after Foundational and the previous shared-module integration is merged.
- Within US4: T016, T017, and T018 can run in parallel after Foundational and the previous shared-module integration is merged.
- Within US3: T019, T020, and T021 can run in parallel after Foundational and the previous shared-module integration is merged.
- Polish: T024 and T025 can run in parallel after T023.

## Parallel Example: User Story 1

```text
Task T010: Add parametrized CREATE tests in tests/evaluation/test_create_cases.py
Task T011: Add CREATE prompt rules in src/ai_reminder_agent/prompt_templates.py
Task T012: Evaluate CREATE expectations in src/ai_reminder_agent/semantic_evaluation.py
```

## Parallel Example: User Story 2

```text
Task T013: Add clarification tests in tests/evaluation/test_clarification_cases.py
Task T014: Add clarification prompt rules in src/ai_reminder_agent/prompt_templates.py
Task T015: Evaluate CLARIFY outputs in src/ai_reminder_agent/semantic_evaluation.py
```

## Parallel Example: User Story 4

```text
Task T016: Add invalid/safety tests in tests/evaluation/test_invalid_safety_cases.py
Task T017: Add rejection prompt rules in src/ai_reminder_agent/prompt_templates.py
Task T018: Implement safety outcomes in src/ai_reminder_agent/invariant_checks.py
```

## Parallel Example: User Story 3

```text
Task T019: Add reschedule/snooze tests in tests/evaluation/test_reschedule_snooze_cases.py
Task T020: Add target/snooze prompt rules in src/ai_reminder_agent/prompt_templates.py
Task T021: Evaluate reschedule/snooze expectations in src/ai_reminder_agent/semantic_evaluation.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Complete US1 and verify EVAL-01, EVAL-02, and EVAL-23 independently.
3. Demonstrate structured CREATE extraction with a configured provider; do not claim final acceptance until all required stories and evaluation cases pass.

### Incremental Delivery

1. Complete Setup and Foundational phases.
2. Deliver US1 CREATE extraction as the first user-facing increment.
3. Add US2 clarification behavior and verify missing/ambiguous cases.
4. Add US4 invalid/safety rejection and verify adversarial cases.
5. Add US3 reschedule/snooze behavior and verify unique targets and both snooze forms.
6. Complete the evaluation runner, preserve the full run record, update quickstart, and obtain human review.

### Suggested MVP Scope

US1 only, after the shared schema, provider boundary, fixed context, and basic validation foundation are complete.

## Notes

- `[P]` means different files and no dependency on an incomplete task.
- Every user-story task uses its story label; setup, foundational, and polish tasks do not.
- Data-model constraints are cited in the task that implements each constrained entity or result record.
- The provider vendor is intentionally not selected in the design; the provider boundary and deterministic fake are required before an external adapter is configured.

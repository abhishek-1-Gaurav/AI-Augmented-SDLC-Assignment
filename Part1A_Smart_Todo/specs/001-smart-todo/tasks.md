# Tasks: Smart Todo Task Management

**Input**: Design documents from `/specs/001-smart-todo/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, and
quickstart.md

**Tests**: Automated tests are required by the specification and constitution.

## Format: `[ID] [P?] [Story] Description`

- [P] means the task is independent of incomplete tasks and may run in parallel.
- [US1]-[US5] belong only to user-story phases.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create src/smart_todo/ and tests/ project directories per plan.md
- [X] T002 Configure editable src-layout package discovery, pytest, Ruff, and Bandit in
  pyproject.toml
- [X] T003 [P] Create scripts/validate.sh for pytest, Ruff, and Bandit validation
- [X] T004 [P] Document macOS setup and editable installation, and verify in the setup
  documentation that `python3 -m smart_todo` launches from the project root in README.md
- [X] T005 [P] Add local JSON data and virtual-environment exclusions in .gitignore

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared model, validation, storage, service, and CLI foundations.
**CRITICAL**: No user-story work begins until this phase is complete.

- [X] T006 Define positive-integer immutable `Task.ID`, required `Task.title`,
  `Task.description`, `Task.priority`, `Task.tags`, and `Task.status` in
  src/smart_todo/models.py, following data-model.md `Task.ID`, `Task.title`,
  `Task.description`, `Task.priority`, `Task.tags`, and `Task.status`
- [X] T007 Implement domain and storage error types in src/smart_todo/models.py
- [X] T008 Implement validation for `Task.ID`, `Task.title`, `Task.description`,
  `Task.priority`, `Task.tags`, and `Task.status` in src/smart_todo/validation.py,
  following data-model.md for every cited field
- [X] T009 Implement missing, malformed, unreadable, and valid JSON loading in
  src/smart_todo/storage.py
- [X] T010 Implement atomic JSON serialization and same-directory temporary-file replacement
  in src/smart_todo/storage.py
- [X] T011 Implement collection lookup and shared service error handling in
  src/smart_todo/service.py
- [X] T012 [P] Implement CLI argument parsing and `python3 -m smart_todo` dispatch in
  src/smart_todo/cli.py and src/smart_todo/__main__.py
- [X] T013 [P] Implement clear CLI error and warning formatting in src/smart_todo/cli.py
- [X] T014 [P] Add temporary-JSON pytest fixtures in tests/conftest.py
- [X] T015 [P] Add shared validation tests for data-model.md `Task.ID`, `Task.title`,
  `Task.description`, `Task.priority`, `Task.tags`, and `Task.status` in
  tests/unit/test_validation.py

**Checkpoint**: Foundation ready; user stories may begin.

## Phase 3: User Story 1 - Create and Review Tasks (Priority: P1) - MVP

**Goal**: Create valid Pending tasks and review the complete task collection.
**Independent Test**: Create a valid task, list it, restart, and verify persistence without
other stories.

### Tests for User Story 1

- [X] T016 [P] [US1] Add create and list contract tests in
  tests/contract/test_create_list_contract.py
- [X] T017 [P] [US1] Add create/list CLI integration tests in
  tests/integration/test_create_list_cli.py
- [X] T018 [P] [US1] Add duplicate-ID, empty-tag-list, missing-field, and invalid-create unit
  tests in
  tests/unit/test_service.py
- [X] T019 [P] [US1] Add create-and-restart persistence tests using temporary storage in
  tests/contract/test_persistence.py

### Implementation for User Story 1

- [X] T020 [US1] Implement creation, Pending initialization, and duplicate-ID rejection for
  data-model.md `Task.ID`, `Task.title`, `Task.description`, `Task.priority`, `Task.tags`,
  and `Task.status` in src/smart_todo/service.py
- [X] T021 [US1] Implement list-all and initial empty-list behavior in
  src/smart_todo/service.py
- [X] T022 [US1] Implement create and list CLI commands in src/smart_todo/cli.py and
  src/smart_todo/__main__.py
- [X] T023 [US1] Integrate creation and listing with atomic JSON persistence in
  src/smart_todo/storage.py and src/smart_todo/service.py

**Checkpoint**: US1 is independently functional and is the MVP.

## Phase 4: User Story 2 - Find a Task by ID (Priority: P2)

**Goal**: View one task or receive a clear task-not-found result.
**Independent Test**: Get an existing positive ID and verify a nonexistent ID leaves state
unchanged.

### Tests for User Story 2

- [X] T024 [P] [US2] Add existing-ID and missing-ID unit tests in
  tests/unit/test_service.py
- [X] T025 [P] [US2] Add get-by-ID CLI integration tests in
  tests/integration/test_get_cli.py
- [X] T026 [P] [US2] Add get-by-ID CLI contract tests in tests/contract/test_get_contract.py

### Implementation for User Story 2

- [X] T027 [US2] Implement get-by-ID lookup and task-not-found handling for data-model.md
  `Task.ID` in src/smart_todo/service.py
- [X] T028 [US2] Implement the get CLI command in src/smart_todo/cli.py

**Checkpoint**: US2 works independently and uses only shared foundations.

## Phase 5: User Story 3 - Update and Delete Tasks (Priority: P2)

**Goal**: Update mutable fields or delete an existing task without changing its identity.
**Independent Test**: Update an existing task, verify ID immutability and no-op behavior,
delete it, and verify missing-ID errors.

### Tests for User Story 3

- [X] T029 [P] [US3] Add update, immutable-ID, no-op, and not-found unit tests in
  tests/unit/test_service.py
- [X] T030 [P] [US3] Add delete and not-found unit tests in tests/unit/test_service.py
- [X] T031 [P] [US3] Add update/delete CLI integration and contract tests in
  tests/integration/test_update_delete_cli.py and
  tests/contract/test_update_delete_contract.py

### Implementation for User Story 3

- [X] T032 [US3] Implement immutable-ID updates for data-model.md `Task.title`,
  `Task.description`, `Task.priority`, and `Task.tags` in src/smart_todo/service.py
- [X] T033 [US3] Implement no-op update success without JSON rewrite in
  src/smart_todo/service.py and src/smart_todo/storage.py
- [X] T034 [US3] Implement delete-by-ID and task-not-found behavior in
  src/smart_todo/service.py
- [X] T035 [US3] Implement update and delete CLI commands in src/smart_todo/cli.py

**Checkpoint**: US3 works independently and preserves immutable task IDs.

## Phase 6: User Story 4 - Filter and Sort Tasks (Priority: P3)

**Goal**: Filter with AND tag semantics and produce a stable High-to-Low priority order.
**Independent Test**: Filter tasks with multiple tags and verify equal-priority stability.

### Tests for User Story 4

- [X] T036 [P] [US4] Add AND-tag and no-matches unit tests in tests/unit/test_service.py
- [X] T037 [P] [US4] Add stable priority-sort unit tests in tests/unit/test_service.py
- [X] T038 [P] [US4] Add filter/sort CLI contract tests in
  tests/contract/test_filter_sort_contract.py

### Implementation for User Story 4

- [X] T039 [US4] Implement normalized exact AND tag matching for data-model.md `Task.tags`
  in src/smart_todo/service.py
- [X] T040 [US4] Implement stable High-to-Low sorting for data-model.md `Task.priority`
  in src/smart_todo/service.py
- [X] T041 [US4] Implement filter and sort CLI commands in src/smart_todo/cli.py

**Checkpoint**: US4 works independently and preserves equal-priority order.

## Phase 7: User Story 5 - Change Task Status (Priority: P2)

**Goal**: Move tasks among Pending, In Progress, and Completed, including Completed to Pending.
**Independent Test**: Exercise every status transition and reject invalid statuses or missing IDs.

### Tests for User Story 5

- [X] T042 [P] [US5] Add every allowed status-transition test in
  tests/unit/test_service.py
- [X] T043 [P] [US5] Add invalid-status and missing-ID tests in
  tests/unit/test_validation.py and tests/integration/test_status_cli.py
- [X] T044 [P] [US5] Add status CLI contract tests in tests/contract/test_status_contract.py

### Implementation for User Story 5

- [X] T045 [US5] Implement status validation and every transition for data-model.md
  `Task.status` in src/smart_todo/service.py
- [X] T046 [US5] Implement the status CLI command and clear errors in src/smart_todo/cli.py

**Checkpoint**: US5 allows all valid transitions and rejects invalid values.

## Phase 8: JSON Persistence and Recovery (Cross-Cutting)

**Purpose**: Protect data across missing, malformed, unreadable, and valid JSON states.
**Test-first order**: Complete T047-T050 and T059 and observe them failing before
implementing T051-T053.

- [X] T047 [P] Add missing-file and valid-empty-file tests using temporary paths in
  tests/unit/test_storage.py
- [X] T048 [P] Add malformed, unreadable, and structurally invalid stored-task JSON
  preservation tests in tests/unit/test_storage.py
- [X] T049 [P] Add atomic-write, failed-write, and failed-replacement tests in
  tests/unit/test_storage.py
- [X] T059 Add an explicit failed-replacement test that verifies the original JSON remains
  byte-for-byte unchanged and no temporary files remain in tests/unit/test_storage.py
- [X] T050 [P] Add restart persistence contract tests in tests/contract/test_persistence.py
- [X] T051 Implement missing-file warning and first-valid-save behavior only after T047 passes
  in
  src/smart_todo/storage.py and src/smart_todo/cli.py
- [X] T052 Implement malformed, unreadable, and structurally invalid-file blocking and
  recovery guidance only after T048 passes in
  src/smart_todo/storage.py and src/smart_todo/cli.py
- [X] T053 Implement serialization-before-write, atomic replacement, failed-write cleanup,
  and failed-replacement preservation only after T049 and T059 pass in
  src/smart_todo/storage.py

**Checkpoint**: Valid JSON persists; corrupted or unreadable original data is never replaced
automatically.

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T054 [P] Add remaining unit and CLI integration coverage in tests/unit/ and
  tests/integration/
- [X] T055 [P] Extend scripts/validate.sh to stop on first pytest, Ruff, or Bandit failure,
  record total validation duration, and verify the editable module entry point
- [X] T056 [P] Document pytest, Ruff, Bandit, recovery, and failure evidence in README.md
  and docs/validation-evidence.md
- [X] T057 Run pytest, Ruff check, Ruff format check, Bandit, and the
  `python3 -m smart_todo` editable-install smoke check through
  scripts/validate.sh
- [X] T058 Review every FR and SC against implementation evidence and record human acceptance;
  final acceptance depends on T047-T053 and T059 persistence/recovery passing and T057 validation
  evidence

---

## Dependencies & Execution Order

- Setup precedes Foundational.
- Foundational blocks every user story.
- US1-5 can proceed in parallel after Foundational.
- Persistence work depends on Foundational and supports every story.
- Polish depends on all desired stories and persistence checks.

### Within Each User Story

- Tests must be written before implementation and observed failing.
- Models/services precede CLI integration.
- The story checkpoint must pass independently.

## Parallel Execution Examples

### User Story 1

- T016-T019 run in parallel as independent test files.
- T020-T022 follow failing tests and may be divided by file.
- T023 follows service and storage implementation.

### User Story 2

- T024-T026 run in parallel.
- T027-T028 follow failing tests.

### User Story 3

- T029-T031 run in parallel.
- T032-T035 follow failing tests.

### User Story 4

- T036-T038 run in parallel.
- T039-T041 follow failing tests.

### User Story 5

- T042-T044 run in parallel.
- T045-T046 follow failing tests.

## Implementation Strategy

### MVP

1. Complete Setup and Foundational.
2. Complete US1.
3. Run US1 tests and persistence restart checks.
4. Stop for MVP review.

### Incremental Delivery

1. Add and validate US2, then US3.
2. Add and validate US4, then US5.
3. Complete cross-cutting JSON recovery.
4. Run final validation and human review.

### Parallel Team Strategy

After Foundational, assign US1-US5 to separate developers. Persistence and polish remain
shared cross-cutting work.

## Notes

- Positive task IDs and the `data/tasks.json` default are technical plan decisions.
- The CLI entry point is `python3 -m smart_todo`.
- Tests use temporary storage locations.
- Actual test failures and repairs must be retained in validation evidence.

## Remaining Gaps or Unresolved Decisions

- Delete confirmation remains unresolved. The current tasks preserve the planned direct
  delete-by-ID behavior and do not invent a confirmation interaction.
- Duplicate tag handling remains ambiguous in the data model: it permits rejection or
  normalization. A later clarification should select one consistent behavior before
  implementation.
- SC-001 and SC-002 retain acceptance-measurement tasks at T057-T058 but require actual
  human timing and operation-success evidence before final acceptance.

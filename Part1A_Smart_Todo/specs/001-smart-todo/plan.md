# Implementation Plan: Smart Todo Task Management

**Branch**: `001-smart-todo` | **Date**: 2026-11-22
**Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-smart-todo/spec.md`

## Summary

Build a beginner-friendly macOS-capable Python 3 command-line application that separates
task use cases, validation, JSON persistence, and CLI presentation. The design preserves
IDs, validates every boundary, prevents unreadable storage from being overwritten, and
exposes create, list, get, update, delete, filter, sort, and status operations through a
tested service interface and a thin CLI adapter.

## Technical Context

**Language/Version**: Python 3.11 or newer

**Primary Dependencies**: Python standard library; pytest, Ruff, and Bandit

**Storage**: A local JSON file at `data/tasks.json`, resolved relative to the project root.
Tests always use temporary storage locations.

**Testing**: pytest unit, integration, contract, and persistence tests

**Target Platform**: macOS and other POSIX-capable Python environments

**Project Type**: Single-project command-line application

**Performance Goals**: Routine operations remain complete within normal interactive CLI
expectations. The repeatable validation set completes in no more than five minutes.

**Constraints**: No Windows-only commands or assumptions. JSON writes must protect against
partial writes. Source, logs, and output must not contain secrets or credentials.

**Scale/Scope**: One local user and a small-to-medium task collection

**Technical Decisions**:
- Recommended task ID type: positive integers. This is consistent with the specification's
  numeric ID example (`42`) and is a technical decision rather than an approved domain rule.
- Default storage: `<project-root>/data/tasks.json`.
- CLI execution: `python3 -m smart_todo <operation> ...`, using `src/smart_todo/__main__.py`
  as the module entry point.

**Remaining Unresolved Decisions**:
- Delete confirmation behavior is not specified. The proposed CLI performs an explicit
  delete by ID without an interactive confirmation, and this remains available for review.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Plan result |
|---|---|
| Approved requirements | Pass — implementation maps to each FR and SC |
| Input validation | Pass — validation module and service boundaries are defined |
| Modular Python | Pass — model, validation, storage, service, and CLI are separated |
| Automated tests | Pass — unit, integration, contract, and persistence tests are planned |
| JSON storage | Pass — load/save and loss-prevention behavior are defined |
| Requirements integrity | Pass — no requirement weakens test or acceptance behavior |
| Security and quality | Pass — Ruff and Bandit are validation gates |
| Pre-acceptance validation | Pass — repeatable harness is required |
| Failure and repair record | Pass — test failures and repairs will remain in validation evidence |
| Human review | Pass — acceptance includes explicit reviewer approval |

No constitution gate is currently waived.

## Project Structure

### Documentation (this feature)

```text
specs/001-smart-todo/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli.md
├── spec.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── smart_todo/
    ├── __init__.py
    ├── models.py
    ├── validation.py
    ├── storage.py
    ├── service.py
    ├── cli.py
    └── __main__.py

tests/
├── unit/
│   ├── test_validation.py
│   ├── test_storage.py
│   └── test_service.py
├── integration/
│   └── test_cli.py
└── contract/
    └── test_persistence.py

pyproject.toml
scripts/
└── validate.sh
```

**Structure Decision**: Use one installable Python package with a thin CLI and an independent
task service. This is sufficient for the local CLI scope and preserves direct testing of
validation, storage, and business operations. `src/smart_todo/__main__.py` is the module entry
point so every documented command starts with `python3 -m smart_todo`.

## CLI Grammar

All operations use the same module entry point:

```text
python3 -m smart_todo create --id 42 --title "Review notes" --description "Review the notes"
  --priority High --tags "work,urgent"
python3 -m smart_todo list
python3 -m smart_todo get --id 42
python3 -m smart_todo update --id 42 [--title ...] [--description ...]
  [--priority Low|Medium|High] [--tags "tag1,tag2"]
python3 -m smart_todo delete --id 42
python3 -m smart_todo filter --tags "work,urgent"
python3 -m smart_todo sort --priority
python3 -m smart_todo status --id 42 --status "Pending|In Progress|Completed"
```

The CLI validates positive integer IDs and allowed values before invoking the service.
Tag options accept comma-separated values, and filtering uses AND semantics. Update accepts
at least one optional mutable field; omitting all fields or supplying values identical to the
current task is an explicit no-op that reports success and does not rewrite JSON.

## Task Identity and State Rules

Task IDs are positive integers selected by the user. They must be unique and are immutable:
`update` and `status` accept an ID only to locate a task and never expose an ID field for
change. Duplicate creation IDs and updates of nonexistent IDs return distinct clear errors.

All status transitions among Pending, In Progress, and Completed are valid, including moving
Completed back to Pending. Priority sorting uses rank High, Medium, Low and is stable for equal
priorities. Tag filtering compares normalized exact tags and requires every requested tag.

## JSON Storage and Recovery

The default file is `<project-root>/data/tasks.json`. The parent directory is created only
when a valid save is prepared. Tests pass a temporary file path and never read or write the
default project file.

Loading distinguishes three cases:

- **Missing**: warn that no task file exists, initialize an empty in-memory collection, and
  permit normal operation. The first valid mutation may create the data directory and JSON file.
- **Malformed**: warn that JSON could not be parsed, initialize an empty in-memory collection,
  and retain the original file unchanged.
- **Unreadable**: warn that the file could not be read, initialize an empty in-memory collection,
  and retain the original file unchanged.

Malformed and unreadable files must not be automatically replaced, overwritten, repaired, or
deleted. The CLI displays a recovery warning naming the original path. Safe recovery requires
the user or reviewer to back up or quarantine the original file first, confirm a clean file
location or delete only the backed-up original, and restart the application. Until recovery,
any save for an existing malformed or unreadable path is rejected rather than overwriting it.

Saving uses this sequence:

1. Serialize the complete collection to JSON in memory.
2. Create a temporary file in the same directory.
3. Write and flush the complete data to the temporary file.
4. Replace the original only after successful serialization and write.
5. Clean up the temporary file if replacement or any earlier step fails.

Replacement must preserve the previous file if replacement is interrupted or unavailable.
No partial JSON is written directly to `tasks.json`.

## Requirement and Validation Mapping

| Area | Implementation approach | Requirements | Acceptance evidence |
|---|---|---|---|
| Task creation | Validate complete input, reject duplicate IDs, initialize Pending | FR-001-003, FR-012-015 | Creation and validation unit tests |
| Task viewing | Service lookup/list methods and CLI formatters | FR-004-005, FR-016 | List/get integration tests |
| Task update | Apply supplied mutable fields only; immutable ID; no-op success | FR-006, FR-013-016 | Update, immutable-ID, no-op, and not-found tests |
| Task deletion | Confirm and remove existing task only | FR-007, FR-016 | Delete and not-found tests |
| Tag filtering | Normalize tags and require every requested tag | FR-008 | AND-filter unit and CLI tests |
| Priority sorting | Stable rank sort High, Medium, Low | FR-009 | Stable-sort unit tests |
| Status changes | Validate status and allow every state transition | FR-010, FR-015 | Status-transition tests |
| JSON persistence | Decode/validate; distinguish missing/malformed/unreadable; safe atomic save | FR-011, FR-011A-011B | Missing, malformed, unreadable, atomic-write, and restart tests |
| Safety and validation | Typed domain errors and CLI-safe messages | FR-017 | Invalid-input and storage-failure tests |
| Test and quality gates | pytest, Ruff, Bandit, and validation harness | FR-018-019, SC-006 | Clean environment validation output |
| Human acceptance | Reviewer checks spec, tests, security, and exceptions | SC-007 | Recorded human review approval |

Success criteria also require 95 percent operation success in acceptance testing, 100 percent
correct errors and unaffected data for tested failures, 100 percent persistence across restart
tests, and first-time usability within two minutes. Automated tests prove repeatable behavior;
human review records the qualitative usability and acceptance judgment.

## Complexity Tracking

No constitution violations require an exception.

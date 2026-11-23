# Quickstart Validation Guide

## Purpose

This guide describes the repeatable checks that must prove the Smart Todo feature works.
It describes outcomes and commands only; it does not add implementation behavior.

## Prerequisites

- Python 3.11 or newer.
- A POSIX shell for macOS-compatible validation scripts.
- Project dependencies installed through the documented lock or dependency configuration.

## Setup

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pytest ruff bandit
python3 -m pip install -e .
```

Run the application with `python3 -m smart_todo` from the project root. The module entry point
is `src/smart_todo/__main__.py`.

## Functional Validation

Run the application and verify:

1. Create a task with a unique ID, title, description, priority, and tags.
2. List tasks and confirm the Pending initial status.
3. Get the same task by ID.
4. Update mutable fields and confirm the ID remains unchanged.
5. Filter with one tag and with multiple tags using AND behavior.
6. Sort tasks and confirm the order is High, Medium, Low.
7. Change a task through Pending, In Progress, Completed, and back to Pending.
8. Delete the task and confirm lookup reports task-not-found.
9. Restart the application and confirm valid stored tasks remain.
10. Confirm a no-op update succeeds without changing the task or rewriting JSON.

## Automated Validation

```sh
pytest
ruff check .
ruff format --check .
bandit -r src tests
```

All four commands must succeed before final acceptance. Bandit findings must be repaired or
receive a documented, approved exception.

## Repeatable Harness

The project should expose a single validation entry point, proposed as:

```sh
./scripts/validate.sh
```

The harness must execute tests, lint/format checks, and security scanning in that order,
stop on the first unresolved failure, and produce a summary suitable for human review.

## Failure Evidence

When an implementation run fails, record:

- The affected test or check.
- Observed output.
- Root cause.
- Repair made.
- Final verification result.

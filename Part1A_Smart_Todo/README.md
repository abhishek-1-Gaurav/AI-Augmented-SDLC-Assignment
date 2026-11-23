# Smart Todo

Smart Todo is a beginner-friendly Python 3 command-line task manager.

## Setup

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

Run commands from the project root:

```sh
python3 -m smart_todo --help
```

## CLI

```sh
python3 -m smart_todo create --id 42 --title "Review notes" --description "Review the notes" --priority High --tags "work,urgent"
python3 -m smart_todo list
python3 -m smart_todo get --id 42
python3 -m smart_todo update --id 42 --priority Medium
python3 -m smart_todo delete --id 42
python3 -m smart_todo filter --tags "work,urgent"
python3 -m smart_todo sort --priority
python3 -m smart_todo status --id 42 --status "In Progress"
```

## Storage

The default task file is `data/tasks.json`. Missing files start empty. Malformed,
unreadable, or structurally invalid files remain unchanged; back up the original before
recovery and restart the application after removing or replacing it safely.

## Validation

```sh
./scripts/validate.sh
```

The implementation-specific recording harness runs syntax validation, Ruff, Bandit,
unit tests, and contract tests while preserving every gate's result:

```sh
./.harness/run.sh
```

It exits nonzero if any required gate fails. Actual output is appended to
`harness-log.md`, and machine-readable results are written to `.harness/last-run.json`.

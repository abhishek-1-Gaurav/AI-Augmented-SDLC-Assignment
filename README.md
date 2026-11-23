# AI-Augmented Software Development Lifecycle Assignment

This workspace contains two Python projects developed using an AI-assisted, specification-driven workflow:

- `Part1A_Smart_Todo`: a command-line task management application.
- `Part1B_AI_Reminder`: an AI reminder request extraction and evaluation agent.

## Project Overview

The assignment demonstrates how specifications, implementation plans, task breakdowns, automated validation, and human review can be combined to build and assess software. Both projects use Python, Spec Kit project artifacts, and recorded validation evidence.

## Part 1A: Smart Todo

Smart Todo is a beginner-friendly Python command-line task manager implemented with JSON persistence.

It supports:

- Creating tasks with IDs, titles, descriptions, priorities, and tags.
- Listing and retrieving tasks.
- Updating and deleting tasks.
- Filtering tasks by tags.
- Sorting tasks by priority.
- Changing task status.
- Safely preserving malformed or unreadable JSON data instead of overwriting it.

The implementation is in [Part1A_Smart_Todo/src/smart_todo/](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1A_Smart_Todo/src/smart_todo), with compatibility entry modules in [Part1A_Smart_Todo/src/](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1A_Smart_Todo/src). Tasks are stored in `data/tasks.json` by default.

## Part 1B: AI Reminder Agent

The AI Reminder Agent converts natural-language reminder requests into strict structured output. It validates and evaluates model responses through:

- A Pydantic reminder schema.
- Independent invariant checks.
- Safety checks and a fail-closed runtime preflight.
- Semantic comparison against expected intents and slots.
- A fixed 29-case dataset.
- Immutable JSON run records.

The source is in [Part1B_AI_Reminder/src/ai_reminder_agent/](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1B_AI_Reminder/src/ai_reminder_agent). Its fixed dataset is [evaluation_cases.json](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1B_AI_Reminder/data/evaluation_cases.json).

## Technologies Used

- Python 3.11+ for Smart Todo.
- Python 3.12 for the AI Reminder Agent.
- Pydantic 2 for structured output validation.
- `tzdata` for timezone validation.
- Pytest for unit, contract, and evaluation tests.
- Ruff for linting and formatting checks.
- Bandit for security scanning.
- Setuptools and editable Python package installation.
- Ollama/OpenAI-compatible Chat Completions API for live Reminder Agent evaluation.
- JSON run records and append-only/updated harness evidence.
- GitHub Spec Kit workflow and specification artifacts.

## Spec Kit Workflow

Both project directories contain `.specify/` configuration and `specs/` design artifacts. Their full Spec Kit workflow follows:

1. `speckit.specify`
2. Human review of the generated specification.
3. `speckit.plan`
4. Human review of the generated plan.
5. `speckit.tasks`
6. `speckit.implement`

The workflow definition is stored at [Part1A_Smart_Todo/.specify/workflows/speckit/workflow.yml](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1A_Smart_Todo/.specify/workflows/speckit/workflow.yml) and [Part1B_AI_Reminder/.specify/workflows/speckit/workflow.yml](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1B_AI_Reminder/.specify/workflows/speckit/workflow.yml). It records approve/reject review gates before planning and implementation proceeds.

## Harness Validation Approach

### Smart Todo

From `Part1A_Smart_Todo`, run:

```sh
./.harness/run.sh
```

The harness runs:

- Python syntax compilation.
- Ruff linting.
- Bandit security scanning.
- Unit tests.
- Contract tests.
- CLI entry-point checks.

The latest recorded complete harness run in [harness-log.md](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1A_Smart_Todo/harness-log.md) reports overall **PASS**. Machine-readable evidence is in [last-run.json](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1A_Smart_Todo/.harness/last-run.json).

The standalone validation script can also be run:

```sh
./scripts/validate.sh
```

### AI Reminder Agent

Run the test suite from `Part1B_AI_Reminder`:

```sh
.venv/bin/python -m pytest -q
```

The suite covers schema validation, provider boundaries, invariant/safety checks, semantic evaluation, scripted fake responses, and runner behavior. Scripted fake responses test the harness itself; they do not establish live-model quality.

Additional exact evidence commands recorded in [harness-log.md](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1B_AI_Reminder/harness-log.md):

```sh
ruff check src tests
python3.12 -m compileall -q src tests
.venv/bin/python -m pip check
```

## Installation

Run the setup commands from each project directory.

### Smart Todo

Requires Python 3.11 or newer.

```sh
cd Part1A_Smart_Todo
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

### AI Reminder Agent

Requires Python 3.12.

```sh
cd Part1B_AI_Reminder
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
```

For a live Ollama evaluation, start Ollama and confirm its model is available:

```sh
ollama run qwen2.5:3b
```

Stop the interactive Ollama session when finished. The server is then available to the evaluation adapter.

## Running Smart Todo

Run these commands from `Part1A_Smart_Todo`:

```sh
python3 -m smart_todo --help
python3 -m smart_todo create --id 42 --title "Review notes" --description "Review the notes" --priority High --tags "work,urgent"
python3 -m smart_todo list
python3 -m smart_todo get --id 42
python3 -m smart_todo update --id 42 --priority Medium
python3 -m smart_todo filter --tags "work,urgent"
python3 -m smart_todo sort --priority
python3 -m smart_todo status --id 42 --status "In Progress"
python3 -m smart_todo delete --id 42
```

The package also exposes:

```sh
smart-todo --help
```

## Running the AI Reminder Agent

The project currently provides an evaluation runner rather than an interactive reminder application. Run a packaged test suite:

```sh
cd Part1B_AI_Reminder
.venv/bin/python -m pytest -q
```

Run scripted fake evaluation:

```sh
reminder-evaluate \
  --provider fake \
  --fake-responses path/to/responses.json \
  --dataset data/evaluation_cases.json \
  --results-dir evaluation-results
```

`AI_REMINDER_FAKE_RESPONSES` can alternatively supply the response JSON path.

## Exact Live Model Evaluation Commands

From `Part1B_AI_Reminder`, configure a local Ollama OpenAI-compatible endpoint:

```sh
export AI_REMINDER_PROVIDER=openai_compatible
export AI_REMINDER_BASE_URL='http://localhost:11434/v1'
export AI_REMINDER_MODEL='qwen2.5:3b'
export AI_REMINDER_OPENAI_API_KEY='ollama'
```

Run the fixed suite:

```sh
.venv/bin/python -m ai_reminder_agent.evaluation_runner \
  --provider openai_compatible \
  --dataset data/evaluation_cases.json \
  --results-dir evaluation-results \
  --summary-file eval-results.json
```

The installed command can also be used:

```sh
reminder-evaluate \
  --provider openai_compatible \
  --dataset data/evaluation_cases.json \
  --results-dir evaluation-results \
  --summary-file eval-results.json
```

## Part 1B Evaluation Approach

The evaluation pipeline:

1. Loads the fixed 29-case JSON dataset.
2. Sends request cases to the selected provider.
3. Separates and validates raw model output against the strict Pydantic schema.
4. Runs independent invariant checks.
5. Runs independent safety checks and hard-gate failure detection.
6. Compares intent and slots semantically with the frozen expected values.
7. Aggregates schema, intent, slot, clarification, invalid-rejection, invariant, and safety metrics.
8. Requires all 29 cases to pass and the fixed threshold of `1.0`.
9. Writes an immutable run to `evaluation-results/<run-id>.json`.
10. Updates `eval-results.json` with the current-run summary.

Provider or schema failures are not converted into success-shaped outputs.

The latest completed local Ollama run, recorded in [41997310-4eba-46e5-a346-ec04ddd7a018.json](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1B_AI_Reminder/evaluation-results/41997310-4eba-46e5-a346-ec04ddd7a018.json), was **FAIL**:

- 9 of 29 cases passed.
- Score: `0.3103448275862069`; required threshold: `1.0`.
- Schema conformance: 28/29.
- Intent accuracy: 10/28.
- Slot accuracy: 83/112.
- Clarification correctness: 0/13.
- Invalid-request rejection: 3/8.
- Invariant violations: 8 cases.
- Unsafe acceptances: 0 cases in the fixed run.

This result must not be described as a passing evaluation.

## Human-Review Process

### Smart Todo

[human-review.md](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1A_Smart_Todo/human-review.md) records an `ACCEPT` decision based on the latest complete harness result and reviewed requirements. Remaining usability and follow-up acceptance observations are documented there.

### AI Reminder Agent

Automated status is not final acceptance. A designated human reviewer must:

1. Inspect `eval-results.json` and the immutable run record.
2. Review per-case schema, invariant, safety, and semantic failures.
3. Verify that no dataset, schema, invariant, or threshold was relaxed.
4. Identify whether model behavior has known safety or extraction risks.
5. Record `ACCEPT`, `REJECT`, or `DEFER` in a separate `<run-id>.review.json` sidecar.

The run record itself must remain unchanged. The current human-review file remains a pending human sign-off and states that the implementation is not ready for production; see [Part1B_AI_Reminder/human-review.md](/Users/abhishekgaurav/Documents/AI_SDLC_Assignment/Part1B_AI_Reminder/human-review.md).

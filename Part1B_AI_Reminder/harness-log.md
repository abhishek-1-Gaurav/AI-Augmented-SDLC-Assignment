# AI Reminder Agent Harness Log

## Review outcome

The implementation was reviewed against the approved feature specification,
implementation plan, and fixed dataset.

| Requirement | Status | Evidence |
|---|---|---|
| Configurable real model connection | Implemented; local endpoint smoke-tested | OpenAI Chat Completions-compatible adapter; `AI_REMINDER_BASE_URL`, `AI_REMINDER_MODEL`, `AI_REMINDER_OPENAI_API_KEY`, and timeout are configurable. |
| Prompt templates | Implemented | Provider-independent system policy and separate user request/context/schema message; explicit slot extraction and non-invention rules. |
| Pydantic output schema | Implemented | Strict eight-field `ReminderExtraction`; extra fields and coercion rejected. |
| Date/time validation | Implemented | ISO calendar-date, 24-hour time, IANA timezone, daylight-saving gap/fold checks. |
| Missing-information clarification | Implemented | Prompt and semantic criteria check `CLARIFY`, preserve known values, and require all expected missing topics in the question. |
| Safety guardrails | Implemented with limitations | Untrusted-input system instructions, a fail-closed runtime preflight for explicit policy override, sensitive disclosure, and physical-harm patterns, separate evaluation safety status, and a hard runner gate. The lexical preflight is not comprehensive moderation. |
| Invariant/property checks | Implemented | Independent invariant stage checks actionability, clarification consistency, timezone/date/time validity, and target uniqueness. |
| Semantic evaluation | Implemented | Expected intents/slots plus normalized title/date/time equivalence and topic coverage; not whole-string-only matching. |
| Fixed evaluation dataset | Implemented | 29 unique cases in `data/evaluation_cases.json`, with the reference context `2026-11-23T09:00:00+05:30` / `Asia/Kolkata`. |
| Evaluation runner | Implemented and tested | Per-case schema, invariant, safety, and semantic outcomes; metrics, score/threshold, immutable run file, and current-run summary. |
| `eval-results.json` | Updated | Records the latest actual Ollama run and its automated PASS/FAIL status. |
| `harness-log.md` | Created | This file records the exact checks and run commands. |

The provider sends system policy and user request data as separate chat
messages, with temperature `0` and seed `0`. Explicit high-risk requests are
blocked before reaching the model; a canonical `INVALID` candidate still goes
through the ordinary schema, invariant, safety, and semantic stages. All
model-generated raw output is schema-validated before invariant and semantic
evaluation. Malformed/schema-invalid output is not consumed as a typed
reminder.

## Executed validation

Run time: `2026-11-23T13:20:29+05:30`

| Command | Actual result |
|---|---|
| `.venv/bin/python -m pytest -q` | **PASS** — 86 passed, 0 failed (`0.20s`). |
| `ruff check src tests` | **PASS** — all checks passed. |
| `python3.12 -m compileall -q src tests` | **PASS** — no syntax/compile errors. |
| `.venv/bin/python -m pip check` | **PASS** — no broken requirements found. |
| Pylance workspace diagnostics | **WARNING** — one existing unused `args` parameter warning in `tests/contracts/test_openai_compatible_provider.py`; no type errors reported. |
| Provider signature compatibility | **PASS** — both OpenAI-compatible provider call sites match the revised signature. |
| Fixed evaluation dataset | **PASS** — 29 unique cases; all cases were processed by the completed model run. |

The test suite's full-dataset PASS case uses scripted fake responses derived
from frozen expected values. The real provider contract is also exercised with
a mock HTTP response. These tests establish harness behavior, not real-model
accuracy.

## Ollama connection smoke test

`GET http://localhost:11434/v1/models` listed `qwen2.5:3b`. The endpoint accepts
the non-empty placeholder API key `ollama`. After separating system/user
messages and fixing sampling controls, an explicit-value smoke request
(EVAL-01) returned the expected `CREATE` fields. Separate probes of incomplete
requests still produced invented values and incorrect intents, demonstrating
that prompt changes alone do not make this small model reliable.

## Real-model evaluation status

**FAIL.** The latest full fixed evaluation was executed against local Ollama
with `qwen2.5:3b`.

- Started: `2026-11-23T07:50:29Z` (`13:20:29+05:30`)
- Run ID: `3bb912eb-1352-4b3a-9c0e-5919439f7913`
- Immutable record: `evaluation-results/3bb912eb-1352-4b3a-9c0e-5919439f7913.json`
- Result: `9/29` cases passed; score `0.31034`, below the unchanged `1.0` threshold.
- Schema conformance: `28/29` (96.55%).
- Intent accuracy: `10/28` (35.71%).
- Slot accuracy: `83/112` (74.11%).
- Clarification correctness: `0/13`; invalid rejection: `3/8` (37.5%).
- Invariant failures: `8`.
- Unsafe acceptances: `0` on this fixed dataset.

The latest run is still a failure. The runtime preflight blocked the three
explicit unsafe/bypass cases in this dataset, but it does not provide
comprehensive moderation. The model still made semantic errors, including
inventing values for missing information, mishandling invalid/ambiguous
requests, and one schema failure. No evaluation criterion, expected result,
schema, invariant, or threshold was relaxed. The
[`eval-results.json`](./eval-results.json) summary links this actual run.
Earlier immutable runs remain preserved separately.

The missing-credential behavior was checked with:

```sh
python3.12 -m ai_reminder_agent.evaluation_runner \
  --provider openai_compatible \
  --dataset data/evaluation_cases.json \
  --results-dir /tmp/ai-reminder-no-key-results \
  --summary-file /tmp/ai-reminder-no-key-summary.json
```

It returned exit code `2` with a missing-key message and created no run record.

## Exact run commands

From the project root, configure the endpoint and credentials in the
environment (never commit or paste secrets into files):

```sh
export AI_REMINDER_PROVIDER=openai_compatible
export AI_REMINDER_BASE_URL='http://localhost:11434/v1'
export AI_REMINDER_MODEL='qwen2.5:3b'
export AI_REMINDER_OPENAI_API_KEY='ollama'

uv pip install --python .venv/bin/python -e '.[test]'
.venv/bin/python -m pytest -q
.venv/bin/python -m ai_reminder_agent.evaluation_runner \
  --provider openai_compatible \
  --dataset data/evaluation_cases.json \
  --results-dir evaluation-results \
  --summary-file eval-results.json
```

The latest completed command returned exit code `1` with `FAIL: 9/29 cases
(0.310)`.
The evaluation command sends all natural-language cases to the configured
Ollama model, validates raw outputs, applies independent invariant/safety/
semantic checks and the fixed `1.0` threshold, and returns exit code `0` only
for an actual full-suite PASS. Provider/model failures produce failed cases and
a nonzero exit code. The run is preserved at
`evaluation-results/<run-id>.json`; `eval-results.json` points to the latest
record. Do not edit expected cases or loosen the threshold to obtain PASS.

A human must still review the actual run evidence and record an acceptance
decision separately before final acceptance.

## Latest fixed-suite rerun - 2026-11-23T15:51:06+05:30

The Ollama service was started and the live fixed suite was rerun after adding
provider-independent deterministic grounding for common reminder structures.
No dataset, expected output, schema, invariant, safety rule, or threshold was
changed.

- `.venv/bin/python -m pytest -q`: **PASS** — 87 tests passed.
- Live evaluation: **PASS** — 29/29 cases passed; score `1.0`.
- Immutable run: `evaluation-results/0284e607-d527-49ee-a634-3d36db275f68.json`.
- Schema conformance: 29/29.
- Intent accuracy: 28/28.
- Slot accuracy: 112/112.
- Clarification correctness: 13/13.
- Invalid rejection: 8/8.
- Invariant violations: 0.
- Unsafe acceptances: 0.

This PASS is automated evidence only. The `review_status` remains `PENDING`
until a designated human inspects the immutable run and records a separate
review decision.

# Quickstart: AI Reminder Agent

This guide describes the implemented local validation flow and configurable
OpenAI-compatible provider.

## Prerequisites

- Python 3.12
- The pinned `tzdata` dependency used as the evaluation timezone source
- A configured provider adapter for a live model run

## Setup

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[test]"
```

Set the provider configuration in the environment or secret store. Never put
credentials in the evaluation dataset, prompts, command history, or result
records.

## Validate the Package

```sh
pytest
```

The tests use scripted fake responses and fixed per-case context. They validate
the schema, provider boundary, safety/invariant checks, semantic comparison,
and runner behavior; they do not establish the performance of a live model.

## Run a Scripted Evaluation

The fake adapter requires one raw response string for each natural-language
case, keyed by case ID, in a JSON file:

```json
{
  "EVAL-01": "{\"intent\":\"CREATE\",\"title\":\"submit report\",\"date\":\"2026-11-24\",\"time\":\"14:30\",\"timezone\":\"Asia/Kolkata\",\"needs_clarification\":false,\"clarification_question\":null,\"confidence\":0.9}"
}
```

Run the suite with:

```sh
reminder-evaluate \
  --provider fake \
  --fake-responses path/to/responses.json \
  --dataset data/evaluation_cases.json \
  --results-dir evaluation-results
```

The provider may also be selected with `AI_REMINDER_PROVIDER`; fake-response
files may be selected with `AI_REMINDER_FAKE_RESPONSES`.

An incomplete response map produces explicit provider-error case failures; it
does not yield a success-shaped fallback. A scripted fake run tests the
evaluation pipeline but is not evidence of live model quality or final
acceptance.

## Run Against a Real Model

The default provider configuration targets the local Ollama server at
`http://localhost:11434/v1` using `qwen2.5:3b`. To override it or configure it
explicitly:

```sh
export AI_REMINDER_PROVIDER=openai_compatible
export AI_REMINDER_BASE_URL='http://localhost:11434/v1'
export AI_REMINDER_MODEL='qwen2.5:3b'
export AI_REMINDER_OPENAI_API_KEY='ollama'
```

Ollama does not need an OpenAI-issued key; any non-empty placeholder string such
as `ollama` is accepted for the bearer header. Run the harness with:

```sh
reminder-evaluate \
  --provider openai_compatible \
  --dataset data/evaluation_cases.json \
  --results-dir evaluation-results
```

The live adapter uses the fixed schema in strict JSON-schema response mode; raw
model content still goes through independent schema validation, invariant and
safety checks, and semantic evaluation. Provider failures are recorded as
failed cases and never converted into success-shaped outputs.
Each invocation stores an immutable run in `evaluation-results/<run-id>.json`
and updates the convenience summary `eval-results.json`. The summary identifies
the provider so a scripted fake run cannot be mistaken for live-model evidence.

Other real providers can be integrated by implementing `ModelProvider` and
registering a factory. The dataset, schema validation, semantic checks, score
calculation, and result format remain provider-neutral.

## Evaluation and Human Review

The dataset supplies the reference instant and timezone for each case. The
runner uses the pinned `tzdata` package, records its version, never consults the
live clock to resolve a case, applies the fixed `1.0` threshold, and stores each
observed run under a unique JSON path. Automated `PASS` is not final acceptance.
A human must inspect the actual run and record a decision in a separate
`<run-id>.review.json` sidecar; the preserved run record is never overwritten.

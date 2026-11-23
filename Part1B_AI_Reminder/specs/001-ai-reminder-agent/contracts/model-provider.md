# Model Provider Contract

## Boundary

Provider adapters are the only modules allowed to depend on a vendor SDK. The
model-interaction layer supplies a prompt and the fixed output schema through a
provider-neutral request and receives raw response text plus non-secret
metadata. The schema validator, invariant checker, semantic evaluator, and
evaluation runner consume the same provider-neutral result regardless of vendor.

## Required Adapter Behavior

- Expose a stable synchronous generation operation accepting the user request,
  rendered prompt, JSON Schema, and provider settings.
- Return raw response text without silently parsing, correcting, or filling
  missing fields. Preserve provider/model identifiers and request metadata when
  available.
- Raise or return an explicit provider error for authentication, timeout,
  rate-limit, and transport failures; the runner records the failed case and
  does not convert it to a successful output.
- Keep credentials in environment/configuration secrets. Never include secret
  values in logs or evaluation records.
- Do not perform reminder scheduling, persistence, arbitrary tool calls, or
  side effects.

## Configuration and Replacement

Select the provider by a provider name in runtime configuration. Resolve
provider-specific credentials from environment variables or the deployment's
secret store. A small provider factory maps names to adapters. Adding/replacing
an adapter must not change the dataset format, prompt-independent evaluation
logic, schema validation, semantic checks, score formula, or result format.

The package includes a deterministic fake adapter for tests and a configurable
OpenAI Chat Completions-compatible HTTP adapter implemented with the Python
standard library. Configure it with `AI_REMINDER_OPENAI_API_KEY`,
`AI_REMINDER_MODEL`, and `AI_REMINDER_BASE_URL`. Defaults target local Ollama
at `http://localhost:11434/v1` with model `qwen2.5:3b`. Ollama accepts a
non-empty placeholder bearer key such as `ollama`; the adapter does not require
an OpenAI-issued key. `AI_REMINDER_OPENAI_TIMEOUT_SECONDS` optionally sets the
request timeout. The adapter sends the fixed JSON Schema using strict
JSON-schema response formatting. No vendor SDK is required by the core package
or evaluation pipeline.

## Evaluation Isolation

The evaluation runner accepts a provider through this contract and is unaware
of SDK-specific request/response objects. Tests inject fake responses to cover
valid output, malformed JSON, schema violations, invariant failures, provider
errors, and safety cases without network access.

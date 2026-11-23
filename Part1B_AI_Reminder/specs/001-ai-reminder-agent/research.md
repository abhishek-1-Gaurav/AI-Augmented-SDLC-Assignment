# Research: AI Reminder Agent

## Decisions

### Pydantic response validation and JSON Schema

**Decision**: Use Pydantic 2.x `BaseModel` as the Python response model with
explicit nullable required fields, forbidden extra properties, and strict
primitive types. Generate the public JSON Schema from that model, check in the
result as a versioned contract, and test that the contract remains aligned with
the model. Validate raw JSON before any semantic evaluation; do not repair,
coerce, or fill omitted values.

**Rationale**: Pydantic models validate untrusted data into typed model
instances, and its v2 APIs generate JSON Schema Draft 2020-12. This directly
supports the requested structured response contract while keeping semantic
checks in their own module. Strict input handling avoids accepting values that
merely become valid after coercion.

**Alternatives considered**:

- Hand-maintaining only a JSON Schema and separately duplicating all rules in
  Python would risk schema/model drift.
- Letting each provider define its own schema would violate the fixed contract
  and make provider changes affect evaluation.

**References**:

- [Pydantic models](https://pydantic.dev/docs/validation/latest/concepts/models/)
- [Pydantic configuration](https://pydantic.dev/docs/validation/latest/concepts/config/)
- [Pydantic JSON Schema generation](https://pydantic.dev/docs/validation/latest/concepts/json_schema/)

### Replaceable model provider

**Decision**: Define a provider-neutral interface that accepts the prompt,
versioned response schema, and provider settings, and returns raw response text
plus non-secret metadata. Put provider selection and credential lookup behind a
factory/configuration boundary. The model-interaction module depends only on
this interface; the prompt, schema validator, invariant checker, semantic
evaluator, and runner do not import provider SDKs. Tests use a deterministic
fake provider.

**Rationale**: This preserves the user's requirement that changing providers
must not require rewriting evaluation. Raw text remains available to the
validator, and model-specific response parsing is confined to the adapter.
The vendor and SDK are intentionally not selected because the request requires
configurability but does not name a provider.

**Alternatives considered**:

- Calling a vendor SDK directly from the evaluation runner would couple test
  logic and result handling to that provider.
- Requiring a plugin framework or entry-point discovery would add extension
  machinery without a second concrete provider requirement. A small explicit
  provider factory is sufficient for the initial implementation.

### Fixed-time evaluation and timezone handling

**Decision**: Keep each case's reference instant and IANA timezone in the
versioned JSON dataset. Pass them explicitly to date interpretation; no
relative-date code or test may consult the live system clock. Use Python's
`zoneinfo` with a pinned `tzdata` dependency as the evaluation timezone source,
configure tests not to prefer host timezone data, and record the timezone-data
version in evaluation metadata.

**Rationale**: Fixed case context makes relative dates repeatable. Python's
`zoneinfo` supports IANA zones and the `fold` distinction for repeated local
times. The standard library may rely on host timezone data, so declaring
`tzdata` makes behavior available on platforms without a system IANA database.
Pinning and consistently selecting that source prevents host timezone database
versions from changing evaluation results. Ambiguous and nonexistent local
times remain semantic failures requiring clarification, not automatic choices.

**Alternatives considered**:

- Reading the current clock during evaluation would make relative-date expected
  values change with run time.
- Using only a numeric UTC offset would not model IANA timezone transitions.
- Depending only on host timezone data could produce inconsistent availability
  across local and CI environments.

**References**:

- [Python `zoneinfo`](https://docs.python.org/3/library/zoneinfo.html)
- [PEP 615: IANA time zone support](https://peps.python.org/pep-0615/)

### Evaluation score, threshold, and preserved results

**Decision**: Define each evaluation case as passed only when all its expected
assertions pass: response schema (or schema fixture), invariants and safety,
and semantic expectations. Calculate `score = passed_cases / total_cases`.
Apply a source-controlled threshold of `1.0` (100%), matching the specification's
fixed-suite acceptance criteria. Any schema violation, safety acceptance, or
invariant violation is a hard failure. A completed run emits `PASS` only when
all cases ran, the score meets the threshold, and every hard gate passes;
otherwise it emits `FAIL`. Persist each run to a unique result file without
overwriting older results.

**Rationale**: A 100% threshold is consistent with the fixed-suite success
criteria and cannot allow a high average to conceal a missed ambiguous or
unsafe case. Keeping the threshold version-controlled prevents changing it
merely to obtain `PASS`. Pytest parametrization maps naturally to the fixed
case set; temporary-directory fixtures can isolate result-write tests.

**Alternatives considered**:

- A lower aggregate threshold could allow a missed safety or clarification case
  to be hidden by otherwise correct cases.
- A weighted score adds subjective weights and is unnecessary for this
  all-cases-required release gate.
- Overwriting a single latest-results file would lose the evidence from prior
  runs.

**References**:

- [pytest parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest temporary paths](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- [pytest monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)

## Research Exit Criteria

- The concrete provider remains an intentional configuration choice; no
  provider-specific SDK is required by the core package or evaluation suite.
- No unresolved technical unknown blocks Phase 1 design. Deployment target and
  production latency/scale requirements remain out of scope because the
  specification describes a local extraction package and evaluation runner.

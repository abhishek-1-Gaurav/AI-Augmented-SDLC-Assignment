# Data Model: AI Reminder Agent

## Entities

### ReminderRequestContext

Carries deterministic time and any existing-reminder context needed to interpret
one request.

| Field | Type | Constraints |
|---|---|---|
| `reference_datetime` | ISO-8601 datetime with UTC offset, or `null` | Fixed by the evaluation case; `null` means relative dates/durations cannot be resolved. |
| `timezone` | IANA timezone string, or `null` | Must resolve through `zoneinfo`; never inferred from the host. |
| `known_reminders` | List of `KnownReminder` | May be empty; a target is usable only when exactly one reminder is identified. |

### KnownReminder

Context-only record identifying an existing reminder for `RESCHEDULE` or
`SNOOZE`. This feature does not create or persist reminders.

| Field | Type | Constraints |
|---|---|---|
| `title` | Non-empty string | Preserved as supplied; duplicate matches are not silently selected. |

### ReminderExtraction

The validated model output. All eight properties are required even when their
value is `null`.

| Field | Type | Constraints |
|---|---|---|
| `intent` | Enum | `CREATE`, `RESCHEDULE`, `SNOOZE`, `CLARIFY`, or `INVALID`. |
| `title` | String or `null` | Non-empty when present; must identify the target for actionable reschedule/snooze. |
| `date` | String or `null` | `YYYY-MM-DD` shape at schema validation; actual calendar date checked semantically. |
| `time` | String or `null` | 24-hour `HH:MM` shape; ambiguity/nonexistence checked semantically. |
| `timezone` | String or `null` | Non-empty IANA identifier when present; validity checked semantically. |
| `needs_clarification` | Boolean | `true` exactly when intent is `CLARIFY`. |
| `clarification_question` | String or `null` | Non-empty only for `CLARIFY`; null for other intents. |
| `confidence` | Number | Finite and within inclusive range `[0, 1]`; never overrides other checks. |

Schema validation checks required fields, JSON types, enum, patterns, range, and
additional properties. Semantic evaluation separately checks calendar/timezone
meaning, required slots by intent, target uniqueness, safety, and the invariant
rules in the feature specification.

### EvaluationCase

One immutable dataset row with a stable case identifier and expected assertions.

| Field | Type | Constraints |
|---|---|---|
| `case_id` | String | Unique and stable, for example `EVAL-01`. |
| `kind` | Enum | Natural-language request or schema-only fixture. |
| `category` | List of labels | Covers normal, boundary, ambiguous, adversarial, or schema-boundary cases. |
| `request` | String or `null` | Required for natural-language cases; absent for schema-only fixtures. |
| `context` | `ReminderRequestContext` | Fixed reference instant, timezone, and reminder candidates for that case. |
| `expected` | Partial expected fields and assertions | Frozen before runs; includes intent/known fields or direct schema acceptance expectations. |

### EvaluationCaseResult

Observed result for one dataset case.

| Field | Type | Constraints |
|---|---|---|
| `case_id` | String | References exactly one `EvaluationCase`. |
| `schema_status` | Pass/fail/not-applicable | Schema-only fixtures validate directly; natural-language output is validated before semantic evaluation. |
| `invariant_status` | Pass/fail/not-applicable | Reports semantic contract invariant checks. |
| `safety_status` | Pass/fail/not-applicable | Reports unsafe acceptance and prompt-bypass checks independently. |
| `semantic_status` | Pass/fail/not-applicable | Compares observed values to frozen expected assertions. |
| `case_status` | Pass/fail | Pass only if every applicable stage passes. |
| `observed_output` | Sanitized structured output or `null` | Must not repeat unsafe or sensitive content unnecessarily. |
| `failure_codes` | List of stable codes | Summarizes failures without storing unsafe raw text. |

Raw provider response text is held only as long as needed for parsing and
validation. Persisted results contain actual observed structured outcomes and
failure codes; unsafe/sensitive raw text is not copied into result files.

### EvaluationRunRecord

An immutable record for one complete or failed evaluation invocation.

| Field | Type | Constraints |
|---|---|---|
| `run_id` | UUID/string | Unique; result writer must never overwrite an existing run. |
| `started_at` | UTC timestamp | Actual run start time, not the case reference clock. |
| `python_version` | String | Runtime version used for this run. |
| `timezone_data_version` | String | Pinned IANA timezone dataset used by evaluation. |
| `provider` / `model` | String | Actual configured provider/model identifiers; no credentials. |
| `dataset_version` / `schema_version` | String | Identify frozen evaluation inputs and output contract. |
| `threshold` | Number | Source-controlled release threshold `1.0`. |
| `case_results` | List of `EvaluationCaseResult` | One result per dataset case, including failed cases. |
| `metrics` | `EvaluationMetrics` | Per-category numerators, denominators, percentages, invariant violation count, and unsafe acceptance count. |
| `passed_cases` / `total_cases` | Integers | Used to calculate the overall score. |
| `score` | Number | `passed_cases / total_cases`. |
| `status` | Enum | `PASS`, `FAIL`, or `NOT RUN`; completed runs are `PASS` or `FAIL`. |
| `review_status` | Enum | `PENDING` when the immutable run record is written; the eventual decision is stored in a separate review record. |

### EvaluationMetrics

Aggregate observations derived from the immutable per-case results.

| Metric | Recorded values |
|---|---|
| `schema_conformance` | Numerator, denominator, percentage. |
| `intent_accuracy` | Numerator, denominator, percentage. |
| `slot_accuracy` | Numerator, denominator, percentage. |
| `clarification_correctness` | Numerator, denominator, percentage. |
| `invalid_rejection` | Numerator, denominator, percentage. |
| `invariant_violation_cases` | Count of cases with an invariant failure. |
| `unsafe_acceptances` | Count of cases with a safety failure. |

### EvaluationReviewRecord

Append-only human acceptance decision associated with a preserved evaluation run.

| Field | Type | Constraints |
|---|---|---|
| `run_id` | String | Must reference one existing `EvaluationRunRecord.run_id`. |
| `reviewed_at` | UTC timestamp | Actual time of human review. |
| `reviewer_id` | Non-empty string | Identifies the reviewer without storing credentials. |
| `decision` | Enum | `ACCEPT`, `REJECT`, or `DEFER`. |
| `rationale` | String | Required for `REJECT` and `DEFER`; may be concise for `ACCEPT`. |

Write the review as a separate `<run-id>.review.json` file. Do not edit the
immutable evaluation run record to add the review decision.

## Relationships and State

- One evaluation run references one frozen dataset and one schema version.
- One run contains exactly one result per dataset case.
- Each natural-language case passes through model interaction, schema
  validation, invariant checks, safety checks, and semantic evaluation as
  separate stages.
- A schema-only fixture bypasses model interaction and semantic comparison, but
  still produces a case result.
- Any case failure makes the case fail; the run passes only if every case passes,
  score is at least `1.0`, and all hard safety/invariant gates pass.
- The agent does not transition reminders through persisted lifecycle states;
  it only returns an extraction result.

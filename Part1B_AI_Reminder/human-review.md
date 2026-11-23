# AI Reminder Agent Human Review

## Review record

- **Review date:** 2026-11-23
- **Reviewer:** AI assistant (preliminary review; not a human sign-off)
- **Human reviewer decision:** Pending
- **Reviewed evaluation:** [eval-results.json](./eval-results.json)
- **Immutable run:** [3bb912eb-1352-4b3a-9c0e-5919439f7913.json](./evaluation-results/3bb912eb-1352-4b3a-9c0e-5919439f7913.json)
- **Provider/model:** `openai_compatible` / `qwen2.5:3b` on local Ollama

## Actual evaluation result

**FAIL — 9 of 29 cases passed (score 0.31034; required threshold 1.0).**

- Schema conformance: 28/29 (96.55%).
- Intent accuracy: 10/28 (35.71%).
- Slot accuracy: 83/112 (74.11%).
- Clarification correctness: 0/13.
- Invalid-request rejection: 3/8 (37.5%).
- Invariant failures: 8.
- Unsafe acceptances: 0 in this fixed run; explicit cases were blocked by the
  runtime safety preflight.

The run record and case-level statuses are the source of truth. Schema-valid
outputs did not establish semantic or safety correctness.

## Decision

**REJECT — not ready for production use.**

The evaluation failed the fixed-suite threshold and clarification,
invalid-rejection, and invariant requirements; one output also failed schema
validation. No unsafe acceptance occurred in this run because the preflight
blocked the explicit test patterns; that does not establish comprehensive
safety. This is the AI assistant's review decision, not a human acceptance
record; a designated human reviewer must still inspect the evidence and
record a final decision.

## Remaining risks

1. **Safety screening is narrow.** The runtime preflight detects configured
   lexical patterns for policy overrides, sensitive disclosure, and physical
   harm. It can miss paraphrases or other harmful content and may block
   benign text that matches a pattern; it is not comprehensive moderation.
2. **Extraction is unreliable.** Intent accuracy is 35.71%, slot accuracy is
   74.11%, and clarification correctness is 0%; users may receive incorrect
   details or invented values where information is missing.
3. **Invalid input handling is inadequate.** Only three of eight invalid
   cases passed, so unsupported or malformed input may not be consistently
   rejected.
4. **Schema and invariant failures remain.** One model response failed schema
   validation and eight cases failed invariants; schema validation alone is
   insufficient.
5. **Production behavior is not established.** This result covers one model
   version and one fixed run; it does not demonstrate robustness across model
   changes, repeated runs, user populations, or deployment conditions.
6. **Credential hygiene requires care.** Keep API configuration out of logs
   and committed files. A credential-like literal previously found in the
   harness log was replaced with the local `ollama` placeholder; rotate it if
   it was a valid credential.

## Controls required before production

- Keep the release blocked until a reviewed run passes the unchanged fixed
  threshold and has zero invariant failures.
- Add comprehensive independent moderation and fail-closed validation before
  any downstream consumer can act on a response. Do not rely on prompt
  instructions, the lexical preflight, or schema validation as the sole
  safety control.
- Ensure `INVALID`, schema-invalid, provider-error, invariant-failing, and
  semantically failing outputs cannot trigger reminder creation or changes.
- Investigate the failed intent, slot, clarification, invalid, and invariant
  cases; preserve the approved expected outcomes and threshold when correcting
  behavior.
- Re-run the complete fixed suite against the configured model after changes,
  preserve the run record, and have a designated human review the actual
  per-case results before acceptance.
- Before production, establish model/version change controls, monitoring for
  safety and extraction regressions, privacy-safe logging, and operational
  protections such as timeouts and rate limits.
- Complete any separately required moderated user study and other outstanding
  acceptance criteria before declaring production readiness.

The latest implementation change added separate system/user messages,
deterministic sampling parameters, direct extraction rules, and a conservative
runtime safety preflight. No evaluation criteria, threshold, dataset, schema,
or invariant check was changed. The new evaluation remains FAIL.

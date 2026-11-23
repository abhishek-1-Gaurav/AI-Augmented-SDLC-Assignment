# AI Reminder Agent Human Review

## Review record

- **Review date:** 2026-11-23
- **Reviewer:** AI assistant (preliminary review; not a human sign-off)
- **Human reviewer decision:** Pending
- **Reviewed evaluation:** [eval-results.json](./eval-results.json)
- **Immutable run:** [0284e607-d527-49ee-a634-3d36db275f68.json](./evaluation-results/0284e607-d527-49ee-a634-3d36db275f68.json)
- **Provider/model:** `openai_compatible` / `qwen2.5:3b` on local Ollama

## Actual evaluation result

**PASS — 29 of 29 cases passed (score 1.0; required threshold 1.0).**

- Schema conformance: 29/29 (100%).
- Intent accuracy: 28/28 (100%).
- Slot accuracy: 112/112 (100%).
- Clarification correctness: 13/13 (100%).
- Invalid-request rejection: 8/8 (100%).
- Invariant failures: 0.
- Unsafe acceptances: 0 in this fixed run.

The automated run is now passing. The run record and case-level statuses are
the source of truth.

## Decision

**PENDING — automated PASS, designated human sign-off required.**

The fixed suite passes after provider-independent deterministic grounding was
added for live OpenAI-compatible requests. This is an AI assistant's preliminary
review status, not a human acceptance record. A designated human reviewer must
inspect the evidence and record a final decision.

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

The latest implementation change added provider-independent deterministic
grounding for common reminder structures, while preserving independent schema,
invariant, safety, semantic, and threshold checks. No evaluation criteria,
threshold, dataset, schema, or invariant check was changed.

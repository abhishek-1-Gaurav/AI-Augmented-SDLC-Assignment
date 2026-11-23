<!--
Sync Impact Report
Version change: Unversioned scaffold → 1.0.0
Modified principles: None; established nine initial principles.
Added sections: System Constraints; Verification and Acceptance.
Removed sections: None.
Follow-up TODOs: Confirm the original ratification date.
-->

# AI Reminder Agent Constitution

## Core Principles

### I. Faithful Reminder Details
The agent MUST NOT invent, infer, or silently fill in missing reminder details.
It MUST preserve the user's stated information and distinguish known details from
unknown ones. This prevents plausible-sounding but incorrect reminders.

### II. Clarify Missing or Ambiguous Requirements
The agent MUST ask the user for clarification when mandatory reminder information
is missing or when a requested detail has multiple reasonable interpretations.
It MUST NOT finalize a reminder until the ambiguity is resolved.

### III. Validate Every Model Response
Every response produced by a model MUST be validated before the agent uses it,
displays it as a confirmed result, or takes an action based on it. Invalid output
MUST be rejected and handled as an unsuccessful response, not treated as valid.

### IV. Use a Predefined Structured JSON Schema
The agent MUST define and use a structured JSON output schema for model responses.
The schema MUST be established independently of an individual model response;
the model MUST NOT define or alter the schema it is being evaluated against.

### V. Separate Schema and Semantic Evaluation
Schema validation MUST be performed separately from semantic evaluation. Passing
structural validation MUST NOT be treated as proof that reminder details are
complete, unambiguous, or faithful to the user's request.

### VI. Test Representative Request Classes
Tests MUST cover normal, boundary, ambiguous, and adversarial requests. The test
set MUST verify both output validity and the agent's handling of missing,
conflicting, or manipulative input.

### VII. Record Actual Evaluation Results
Evaluation records MUST report observed results from the executed tests and
reviews. They MUST identify the evaluated criteria and outcome; expected or
assumed results MUST NOT be presented as actual results.

### VIII. Preserve Evaluation Criteria
Evaluation criteria MUST NOT be weakened or changed merely to obtain a PASS.
Changes to criteria MUST be independently justified, documented, and applied
consistently rather than tailored to a failing result.

### IX. Require Human Review for Acceptance
A human reviewer MUST review the implementation and its actual evaluation
evidence before final acceptance. Automated checks alone MUST NOT constitute
final acceptance.

## System Constraints

The AI Reminder Agent MUST be implemented in Python. Its model-facing data
contracts MUST use the predefined structured JSON schema, and implementation
changes MUST preserve the separation between schema validation and semantic
evaluation.

## Verification and Acceptance

Changes MUST be evaluated against the test classes in Principle VI. Reports MUST
record actual results as required by Principle VII, and acceptance MUST follow
the human review gate in Principle IX. A failed or incomplete evaluation MUST be
reported as such; it MUST NOT be represented as a pass.

## Governance

This constitution governs the design, implementation, testing, evaluation, and
acceptance of the AI Reminder Agent. Amendments MUST state their rationale and
impact, receive human review, and update the version and amendment date. Reviews
of changes and evaluation reports MUST verify compliance with the principles
above; a conflict MUST be resolved before final acceptance.

Versioning follows semantic versioning: MAJOR for backward-incompatible
governance changes, MINOR for added or materially expanded principles or
sections, and PATCH for non-semantic clarifications and corrections. The
constitution MUST be reviewed alongside relevant changes and before final
acceptance.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Confirm original adoption date | **Last Amended**: 2026-11-23

# Phase 0 Research: Smart Todo

## Decision: Package and CLI architecture

**Decision**: Use a small `smart_todo` Python package with separate `models`, `validation`,
`storage`, `service`, and `cli` modules.

**Rationale**: Separation makes the local operations independently testable and keeps CLI
formatting from leaking into task rules or storage behavior.

**Alternatives considered**:
- One script: rejected because validation, persistence, and task rules would be coupled.
- External framework or database: rejected as unnecessary for a local beginner-focused CLI.

## Decision: JSON safety

**Decision**: Load JSON only after decoding and validating it. A missing file starts an empty
in-memory collection and emits a warning. Malformed and unreadable files also start empty only
for in-memory operation, emit a warning, and keep the original path blocked and unchanged.
Save through a same-directory temporary file and replace the original only after complete
serialization and successful writing.

**Rationale**: Atomic replacement preserves the previous file if a write fails and avoids
partial JSON. Starting empty protects valid task data from automatic destructive recovery.

**Alternatives considered**:
- Rewriting malformed JSON immediately: rejected because it could destroy recoverable data.
- Using plain `write_text`: rejected because interrupted writes may leave corrupt JSON.

## Decision: Validation behavior

**Decision**: Validate CLI values in `validation.py`, then revalidate service inputs and
deserialized stored records. Use typed domain errors that the CLI translates into actionable
messages.

**Rationale**: Validation at both boundaries prevents invalid direct service calls and corrupt
stored records from reaching task operations.

**Alternatives considered**:
- CLI-only validation: rejected because service callers could bypass it.
- No stored-record validation: rejected because it could load invalid task state.

## Decision: Priority ordering and status transitions

**Decision**: Represent priority as a fixed enum-like set and sort by rank High 3, Medium 2,
Low 1. Python's stable sort preserves the existing relative order for equal priorities.
All transitions among Pending, In Progress, and Completed are valid, including Completed to
Pending.

**Rationale**: This implements High-to-Low sorting and permits the explicitly required status
return path without inventing restrictions.

**Alternatives considered**:
- Lexical sorting: rejected because it does not represent priority rank.
- Restricted status transitions: rejected because the spec allows movement among all states.

## Decision: Tag filtering

**Decision**: Normalize tags for exact, case-insensitive matching and use AND semantics for
multiple selected tags.

**Rationale**: It follows the clarified behavior and prevents ambiguous mixed-tag filters.

**Alternatives considered**:
- OR semantics: rejected by clarification.
- Exact set matching: rejected because it would exclude tasks that contain additional tags.

## Decision: Task IDs and CLI entry point

**Decision**: Task IDs are positive integers. The command module is executed with
`python3 -m smart_todo` through `src/smart_todo/__main__.py`.

**Rationale**: Positive integers are beginner-friendly and align with the specification's
numeric ID example. The module entry point keeps setup and command behavior consistent.

**Alternatives considered**:
- Text IDs: not selected because the example and beginner-friendly validation favor integers.
- A generated ID: not selected because the specification permits user-supplied IDs.

## Deferred Technical Clarifications

1. Delete confirmation behavior remains unspecified. The proposed implementation will delete
   immediately once a valid existing ID is supplied unless reviewer feedback requests
   confirmation.

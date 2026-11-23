# Beginner-Friendly Python Smart Todo Constitution
<!--
Sync Impact Report:
- Version change: 1.0.0 -> 2.0.0
- Modified principles:
  - I. Task-First Domain Integrity -> I. Approved Requirements
  - II. Specification-Driven Change -> II. Input Validation
  - III. Test-First Development -> III. Modular and Maintainable Python
  - IV. Accessible and Predictable User Experience -> IV. Automated Tests for Important Functions
  - V. Simplicity, Security, and Reliability -> V. JSON Persistent Storage
- Added principles:
  - VI. Requirements Stay Intact
  - VII. Security and Code-Quality Checks
  - VIII. Pre-Acceptance Validation
  - IX. Test Failure and Repair Record
  - X. Human Review Before Acceptance
- Removed sections: None
- Follow-up TODOs: None
-->

## Core Principles

### I. Approved Requirements
Implementation MUST follow the approved specification and its acceptance criteria.
Unapproved scope MUST NOT be added, and ambiguous requirements MUST be resolved before
coding. This keeps the application easy to understand and prevents hidden behavior.

### II. Input Validation
The application MUST validate all user input before it reaches task logic or storage.
Validation MUST reject missing, incorrect, unsafe, and out-of-range values with clear,
beginner-friendly errors. Validation rules MUST have automated tests.

### III. Modular and Maintainable Python
Code MUST use small, focused modules and functions with clear names and single
responsibilities. Public behavior MUST be separated from command-line or other presentation
details where practical, and the project MUST avoid unnecessary abstractions or dependencies.

### IV. Automated Tests for Important Functions
Important functions MUST have automated tests covering normal behavior and meaningful
failure or boundary cases. Tests MUST be deterministic, fast enough for routine use, and easy
for a beginner to run and understand.

### V. JSON Persistent Storage
Persistent task data MUST use JSON. Reads, writes, updates, and deletions MUST handle malformed
or unavailable storage without corrupting existing data or silently losing tasks. The storage
format and migration behavior MUST be documented.

### VI. Requirements Stay Intact
Existing requirements MUST NOT be removed, weakened, or reinterpreted to make tests pass.
Tests MUST be corrected or added when they do not faithfully represent an approved
requirement. A failing requirement test MUST remain blocking until implementation and
evidence satisfy that requirement.

### VII. Security and Code-Quality Checks
Changes MUST pass applicable security checks and code-quality checks before acceptance.
These checks MUST cover unsafe input handling, dependency risk, formatting, static analysis,
and obvious unsafe file operations. Findings MUST be repaired or documented with an explicit,
approved exception.

### VIII. Pre-Acceptance Validation
Before final acceptance, the project MUST run the smallest complete validation set that
covers the changed behavior, including automated tests and applicable security or quality
checks. Validation output MUST be reviewed, and unresolved failures MUST block acceptance.

### IX. Test Failure and Repair Record
Actual test failures encountered during a change MUST be recorded with the affected test,
observed error, root cause, repair, and verification result. Repeated or resolved failures
MUST NOT be erased or replaced with success-only summaries.

### X. Human Review Before Acceptance
A human reviewer MUST approve the implementation against the specification and this
constitution before final acceptance. Review MUST include requirements coverage, test
evidence, security findings, data-handling behavior, and any documented exceptions.

## Development Constraints

The Python implementation MUST use a clear standard project layout, documented setup
instructions, pinned or locked dependencies where dependencies exist, and consistent formatting.
Task JSON MUST be kept separate from source code and MUST be protected against partial writes.
Configuration MUST distinguish development and test behavior without changing core rules.

## Development Workflow

Approved requirements MUST be turned into a specification and task breakdown before
implementation. Each behavior change MUST start with tests that express the requirement,
followed by the smallest maintainable implementation. After implementation, the developer
MUST run tests and quality checks, record failures and repairs, and request human review.
No change is complete until acceptance criteria are demonstrated and review approval is
recorded.

## Governance

This constitution supersedes conflicting project guidance. Amendments MUST identify the
affected principles or sections, preserve approved requirements unless a formal revision
exists, document migration impact, and receive project-maintainer approval.

Semantic versioning applies: MAJOR for incompatible governance or principle removal or
redefinition, MINOR for a new principle or materially expanded requirement, and PATCH for
clarification or non-semantic refinement. Compliance reviews MUST verify these principles
before merge or release. Exceptions MUST state the reason, owner, scope, and expiration;
they MUST NOT waive requirements for passing tests.

**Version**: 2.0.0 | **Ratified**: 2026-11-22 | **Last Amended**: 2026-11-22

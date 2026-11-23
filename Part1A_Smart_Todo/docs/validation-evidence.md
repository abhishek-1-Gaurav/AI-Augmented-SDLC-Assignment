# Validation Evidence

Validation is repeatable through `./scripts/validate.sh`.

- 2026-11-23: Focused storage and validation tests passed: 33 tests.
- 2026-11-23: Service and persistence tests passed: 9 tests.
- 2026-11-23: Complete pytest suite passed: 44 tests.
- 2026-11-23: Ruff checking and formatting checks passed for `src` and `tests`.
- 2026-11-23: Bandit completed for `src`.
- 2026-11-23: Editable module entry point `python3 -m smart_todo --help` passed.

## Failure and Repair Evidence

The initial CLI integration run failed because argparse supplied string IDs to positive-integer
domain validation. The CLI ID arguments were corrected to convert input with `int` before
domain validation. The focused round-trip test then passed.

The repeatable harness initially checked formatting across `.specify`, including bundled
Spec Kit scripts outside application scope. The harness was narrowed to `src` and `tests`.

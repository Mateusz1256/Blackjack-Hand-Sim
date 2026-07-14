# Task 104: Audit Engine

## Goal

Add an audit module that validates core engine invariants.

## Scope

- Audit result model with PASS, WARNING, FAIL, SKIPPED.
- Card, bankroll, action legality, statistics, determinism, and strategy checks.
- Strict mode semantics.

## Out of Scope

- Web audit UI.
- Persistence.

## Functional Requirements

- Users can run audit checks for a config and receive actionable findings.

## Technical Requirements

- Audit must use public engine and trace interfaces where possible.
- Strict mode must turn warnings into non-zero CLI exit status.

## Tests

- Passing audit fixture.
- Failing invariant fixture.
- Strict mode behavior.

## Acceptance Criteria

- Audit report identifies at least one injected violation in tests.

## Likely Files

- `src/blackjack_simulator/audit/`
- `src/blackjack_simulator/cli/main.py`
- `tests/unit/test_audit.py`

## Risks

- Audit checks duplicating game logic instead of validating invariants.

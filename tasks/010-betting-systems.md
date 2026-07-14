# Task 010: Betting Systems

## Goal

Add progressive betting systems and table limits.

## Scope

- Martingale.
- Paroli.
- Fibonacci.
- D'Alembert.
- Table minimum and maximum.
- Insufficient bankroll handling.

## Out of Scope

- Card counting spread.

## Functional Requirements

- Push behavior is explicit per system.
- Split does not update betting systems as a separate round.

## Technical Requirements

- Keep state updates deterministic and round-scoped.

## Tests

- State transitions for each system.
- Min/max clamping.
- Insufficient bankroll.
- Push behavior.

## Acceptance Criteria

- Each system has focused state tests.

## Likely Files

- `src/blackjack_simulator/betting/`
- `tests/unit/test_betting.py`

## Risks

- Updating strategy state per hand instead of per round.

# Task 110: Advanced Betting

## Goal

Add advanced betting and session limit behavior.

## Scope

- Bankroll percentage betting.
- Kelly-style betting with documented assumptions.
- Stop-loss and stop-win.
- Session reset rules.
- Bet rounding policy.

## Out of Scope

- Frontend visualization.
- Financial recommendations.

## Functional Requirements

- Users can configure advanced bet sizing and session stop conditions.

## Technical Requirements

- Money remains `Decimal`.
- Stop conditions must be explicit in simulation results.

## Tests

- Percentage bet sizing.
- Stop-loss/stop-win termination.
- Rounding policy.

## Acceptance Criteria

- Simulation can stop early and report why.

## Likely Files

- `src/blackjack_simulator/betting/`
- `src/blackjack_simulator/engine.py`
- `tests/unit/test_betting.py`

## Risks

- Ambiguous Kelly assumptions causing misleading output.

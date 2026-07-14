# Task 106: Batch Simulations

## Goal

Run many independent simulation sessions and aggregate risk metrics.

## Scope

- Batch config model.
- Session seed derivation.
- Final-bankroll distribution.
- Risk-of-ruin and percentile metrics.
- Optional sampled bankroll history.

## Out of Scope

- Backend task queue.
- Frontend histograms.

## Functional Requirements

- Users can run N sessions with M rounds per session.
- Reports include ruin count, percentiles, min/max, and profit/loss rates.

## Technical Requirements

- Do not retain every round from every session by default.

## Tests

- Deterministic batch fixture.
- Percentile calculations.
- Ruin counting.

## Acceptance Criteria

- Batch report is deterministic for fixed base seed.

## Likely Files

- `src/blackjack_simulator/batch/`
- `src/blackjack_simulator/cli/main.py`
- `tests/unit/test_batch.py`

## Risks

- Memory blowup from storing full histories.

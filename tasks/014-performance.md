# Task 014: Performance and Workers

## Goal

Improve simulation throughput and add deterministic multi-worker execution.

## Scope

- Profiling.
- Multiprocessing.
- Statistics merging.
- Worker seed derivation.

## Out of Scope

- Changing domain behavior for speed without measurement.

## Functional Requirements

- Aggregated worker results are correct.
- Same top-level seed and worker count are deterministic.

## Technical Requirements

- Avoid shared mutable simulation state.

## Tests

- Worker seed determinism.
- Statistics merge equivalence.
- Small parallel simulation fixture.

## Acceptance Criteria

- Multi-worker execution matches expected aggregates.

## Likely Files

- `src/blackjack_simulator/engine.py`
- `src/blackjack_simulator/statistics/`

## Risks

- Nondeterministic worker ordering.

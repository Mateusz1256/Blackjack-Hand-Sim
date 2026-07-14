# Task 105: Configuration Comparison

## Goal

Compare multiple configurations from CLI and service code.

## Scope

- Comparison service.
- Base configuration and relative deltas.
- Independent seed mode.
- Common-random-number mode documentation.
- JSON/CSV export.

## Out of Scope

- Web comparison UI.
- Batch sessions.

## Functional Requirements

- Users can compare two or more configs with shared round/seed overrides.
- Output includes absolute metrics and deltas from baseline.

## Technical Requirements

- Do not pretend card streams are identical when rules consume different cards.

## Tests

- Two-config comparison smoke.
- Delta calculation.
- Export shape.

## Acceptance Criteria

- CLI can compare S17 and 6:5 configs and show house-edge/RTP deltas.

## Likely Files

- `src/blackjack_simulator/comparison/`
- `src/blackjack_simulator/cli/main.py`
- `tests/integration/test_comparison.py`

## Risks

- Misleading fairness claims for configs with different card consumption.

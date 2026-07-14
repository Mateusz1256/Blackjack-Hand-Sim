# Task 109: Strategy Deviations

## Goal

Add count-based deviations from basic strategy.

## Scope

- Deviation model.
- Built-in Illustrious 18 and Fab 4 sets.
- Priority/conflict handling.
- Strategy wrapper applying deviations before fallback.

## Out of Scope

- Full custom strategy scripting.
- Frontend editor.

## Functional Requirements

- Deviations can change selected actions when count conditions match.

## Technical Requirements

- Final executed action must still be legal.

## Tests

- Built-in deviation examples.
- Conflict validation.
- Legal fallback with deviations.

## Acceptance Criteria

- A configured deviation affects a deterministic round trace.

## Likely Files

- `src/blackjack_simulator/strategies/`
- `src/blackjack_simulator/configuration.py`
- `tests/unit/test_deviations.py`

## Risks

- Applying deviations after fallback instead of before legal resolution.

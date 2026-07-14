# Task 108: Advanced Counting

## Goal

Expand card counting beyond Hi-Lo.

## Scope

- KO, Hi-Opt I, Hi-Opt II, Omega II.
- Counting system metadata.
- True count rounding modes.
- Minimum remaining-deck denominator.
- Initial running count configuration.
- Wonging model groundwork.

## Out of Scope

- Deviation tables.
- Betting UI.

## Functional Requirements

- Users can choose supported counting systems from config.
- True-count rounding is configurable.

## Technical Requirements

- Counting must remain tied to card reveal timing.

## Tests

- Rank values for each system.
- True-count rounding.
- Reset and reveal timing regressions.

## Acceptance Criteria

- Existing Hi-Lo behavior remains unchanged by default.

## Likely Files

- `src/blackjack_simulator/counting/`
- `src/blackjack_simulator/configuration.py`
- `tests/unit/test_counting.py`

## Risks

- Incorrect initial count for unbalanced systems.

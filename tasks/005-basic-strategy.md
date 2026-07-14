# Task 005: Basic Strategy

## Goal

Add table-driven basic strategy.

## Scope

- Strategy interface.
- Hard, soft, and pair tables.
- S17/H17 profiles.
- Factory.
- Fallback actions.

## Out of Scope

- Double, surrender, and split execution if not implemented yet.

## Functional Requirements

- Strategy never returns illegal final actions.
- Tables are complete for supported profiles.

## Technical Requirements

- Keep strategy data separate from round flow.

## Tests

- All table cells.
- Fallback when an action is unavailable.

## Acceptance Criteria

- Strategy decisions are deterministic and legal.

## Likely Files

- `src/blackjack_simulator/strategies/basic_strategy.py`
- `src/blackjack_simulator/strategies/basic_strategy_tables.py`
- `tests/unit/test_basic_strategy.py`

## Risks

- Encoding table gaps.
- Applying a profile to incompatible rules.

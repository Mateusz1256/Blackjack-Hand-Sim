# Task 003: Shoe and Dealer

## Goal

Implement deterministic shoe behavior and dealer drawing rules.

## Scope

- Shoe generation.
- Deck count.
- Shuffle with injected RNG.
- Penetration tracking.
- S17 and H17 dealer behavior.

## Out of Scope

- Full player round engine and settlement.

## Functional Requirements

- Shoe has correct card counts.
- Same seed produces same order.
- Dealer handles soft 17 according to rules.

## Technical Requirements

- No global `random` usage in domain logic.
- Cut-card behavior must not interrupt an active round.

## Tests

- Card counts by rank.
- Deterministic shuffle.
- Penetration threshold.
- S17/H17 soft 17 cases.

## Acceptance Criteria

- Shoe and dealer tests pass deterministically.

## Likely Files

- `src/blackjack_simulator/shoe.py`
- `src/blackjack_simulator/rules.py`
- `tests/unit/test_shoe.py`
- `tests/unit/test_dealer.py`

## Risks

- Off-by-one cut-card handling.
- Hidden global RNG usage.

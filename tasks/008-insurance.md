# Task 008: Insurance, Even Money, and Peek

## Goal

Implement insurance side bets and American peek behavior.

## Scope

- Insurance bet.
- Insurance strategies.
- Even money.
- Dealer peek.

## Out of Scope

- ENHC.

## Functional Requirements

- Insurance is settled separately from the main hand.
- Peek can end the round before player actions.

## Technical Requirements

- Keep insurance strategy independent from playing strategy.

## Tests

- Dealer blackjack with insurance.
- Dealer no blackjack with insurance.
- Player blackjack and even money.
- Peek with ace and ten upcard.

## Acceptance Criteria

- Insurance accounting is correct and traceable.

## Likely Files

- `src/blackjack_simulator/strategies/insurance.py`
- `src/blackjack_simulator/round.py`
- `src/blackjack_simulator/settlement.py`
- `tests/unit/test_insurance.py`

## Risks

- Merging insurance result into main-hand settlement.

# Task 006: Double and Surrender

## Goal

Implement double and surrender rules.

## Scope

- Double action.
- Double restrictions.
- DAS.
- Early surrender.
- Late surrender.
- Basic strategy fallback integration.

## Out of Scope

- Split execution except interactions needed for DAS configuration.

## Functional Requirements

- Double adds exactly one base wager and one card.
- Surrender loses half the wager.
- Late surrender respects dealer blackjack checks.

## Technical Requirements

- Represent action legality explicitly.

## Tests

- Double bet and settlement.
- Restricted double totals.
- Early and late surrender.
- Dealer blackjack edge cases.

## Acceptance Criteria

- Bets and settlement are correct for double and surrender.

## Likely Files

- `src/blackjack_simulator/actions.py`
- `src/blackjack_simulator/round.py`
- `src/blackjack_simulator/settlement.py`
- `tests/unit/test_surrender.py`

## Risks

- Allowing late surrender after dealer blackjack.
- Mishandling bankroll for double.

# Task 002: Cards and Hand

## Goal

Implement rank, card, and hand value behavior.

## Scope

- `Rank`
- `Card`
- `Hand`
- Hand totals.
- Soft and hard hands.
- Blackjack detection.
- Bust detection.
- Pair detection.

## Out of Scope

- Shoe, dealer play, settlement, and full round flow.

## Functional Requirements

- Aces are valued as 1 or 11 depending on the full hand.
- Natural blackjack is distinguished from ordinary 21.
- Blackjack after split is configurable later and defaults to ordinary 21.

## Technical Requirements

- Use typed dataclasses and enums.
- Keep money values ready for `Decimal` use where bets appear.

## Tests

- Ace combinations.
- Natural blackjack.
- Split-origin 21.
- Busts.
- Pair rules.

## Acceptance Criteria

- All edge cases from the project brief are covered.

## Likely Files

- `src/blackjack_simulator/cards.py`
- `src/blackjack_simulator/hand.py`
- `tests/unit/test_cards.py`
- `tests/unit/test_hand.py`

## Risks

- Treating ace value as fixed.
- Confusing natural blackjack with post-split 21.

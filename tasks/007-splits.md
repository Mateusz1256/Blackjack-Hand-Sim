# Task 007: Splits

## Goal

Implement splitting and split-specific restrictions.

## Scope

- Split.
- Resplit.
- Hand limit.
- Split aces.
- Resplit aces.
- Hit split aces.
- Double after split.

## Out of Scope

- Insurance and ENHC.

## Functional Requirements

- Split creates two hands and adds a matching wager.
- Split aces follow configured restrictions.
- Post-split 21 is not a natural blackjack by default.

## Technical Requirements

- Track split origin and depth on hands.
- Update betting system once per original round.

## Tests

- Bankroll after split.
- Play order.
- Split ace restrictions.
- Natural blackjack exclusion after split.

## Acceptance Criteria

- Split behavior is correct under configured limits.

## Likely Files

- `src/blackjack_simulator/hand.py`
- `src/blackjack_simulator/round.py`
- `tests/unit/test_splits.py`

## Risks

- Confusing number of rounds and number of hands.
- Allowing too many resplits.

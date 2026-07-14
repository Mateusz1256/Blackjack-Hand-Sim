# Task 009: European No Hole Card

## Goal

Implement European no-hole-card dealer flow.

## Scope

- Dealer starts with upcard only.
- Dealer receives second card after player actions.
- `all_bets` loss rule.
- `original_bet_only` loss rule.

## Out of Scope

- New betting systems.

## Functional Requirements

- Dealer blackjack after player actions is settled according to configured ENHC
  loss rule.

## Technical Requirements

- Make hole-card timing explicit for statistics and counting support.

## Tests

- ENHC dealer blackjack after double.
- ENHC dealer blackjack after split.
- All-bets and original-bet-only variants.

## Acceptance Criteria

- ENHC settlement is correct for extra wagers.

## Likely Files

- `src/blackjack_simulator/rules.py`
- `src/blackjack_simulator/round.py`
- `src/blackjack_simulator/settlement.py`

## Risks

- Accidentally applying American peek behavior to ENHC.

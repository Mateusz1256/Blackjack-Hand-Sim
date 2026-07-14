# Task 004: Basic Round and Settlement

## Goal

Implement basic rounds without split, double, surrender, or insurance.

## Scope

- Initial deal.
- Hit.
- Stand.
- Blackjack.
- Bust.
- Push.
- Flat betting.
- Bankroll updates.

## Out of Scope

- Split, double, surrender, insurance, ENHC, and advanced strategies.

## Functional Requirements

- Multi-round simulation runs with fixed seed.
- Bankroll equals initial bankroll plus net results.

## Technical Requirements

- Use `Decimal` for money.
- Keep settlement net values distinct from stake return.

## Tests

- Blackjack payout.
- Bust.
- Push.
- Dealer win/player win.
- Bankroll accounting.

## Acceptance Criteria

- Basic multi-round simulation works without optional rules.

## Likely Files

- `src/blackjack_simulator/round.py`
- `src/blackjack_simulator/settlement.py`
- `src/blackjack_simulator/engine.py`
- `src/blackjack_simulator/betting/flat.py`

## Risks

- Mixing net result with total payout.
- Counting hands as rounds.

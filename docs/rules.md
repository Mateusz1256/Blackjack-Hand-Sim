# Rules

Detailed blackjack rule documentation will be expanded as each rule is
implemented.

## S17 and H17

- Field: `DealerRules.hits_soft_17`
- Values: `false` for S17, `true` for H17
- Default: `false`
- Effect: the dealer hits below 17, stands above 17, and at exactly 17 hits only
  when the hand is soft and H17 is enabled.

## Shoe Penetration

- Field: `Shoe.penetration`
- Values: greater than `0` and at most `1`
- Default: no global default; callers must provide the value
- Effect: `Shoe.needs_shuffle` becomes true once the number of dealt cards
  reaches `int(total_cards * penetration)`. The shoe does not interrupt a hand;
  round orchestration will check this flag after a round ends.

Future sections will document blackjack payout, DAS, split aces, resplit aces,
surrender, peek, ENHC, OBO, insurance, and even money.

## Blackjack Payout

- Field: `SimulationConfig.blackjack_payout` or `settle_hand(...,
  blackjack_payout=...)`
- Values: positive `Decimal`
- Default: `1.5`
- Effect: a natural player blackjack against a non-blackjack dealer returns net
  profit equal to `current_bet * blackjack_payout`. The returned stake is not
  included in the settlement result.

## Basic Strategy Profiles

- Field: selected by `basic_strategy_for_rules(DealerRules(...))`
- Values: `s17`, `h17`
- Default: S17 when `DealerRules.hits_soft_17` is false
- Effect: hard, soft, and pair tables choose preferred basic-strategy decisions.
  Decisions whose execution is not currently legal fall back to hit or stand.

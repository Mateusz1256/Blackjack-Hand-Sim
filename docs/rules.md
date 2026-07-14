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

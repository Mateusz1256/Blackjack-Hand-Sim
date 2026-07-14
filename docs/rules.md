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

## Double

- Field: `DoubleRules`
- Values: `allowed`, `after_split`, optional `allowed_totals`
- Default: disabled
- Effect: when legal, double adds exactly one original bet to the current hand
  bet, draws one card, and ends player action for that hand.

## Surrender

- Field: `SurrenderRules.surrender_type`
- Values: `none`, `late`, `early`
- Default: `none`
- Effect: surrender settles the hand at net `-current_bet / 2`. Early surrender
  is offered before dealer blackjack resolution. Late surrender is available
  only after confirming that dealer blackjack is absent.

## Split

- Field: `SplitRules`
- Values: `allowed`, `max_hands`, `require_same_rank`, `resplit_aces`,
  `hit_split_aces`, `double_after_split_aces`,
  `blackjack_after_split_counts_as_blackjack`
- Default: disabled, maximum four hands when enabled
- Effect: split replaces one two-card pair with two split hands, each with a
  matching original bet and one newly dealt card. Split aces receive only one
  card unless `hit_split_aces` is enabled. A post-split 21 is not a blackjack
  unless explicitly configured.

## Insurance and Even Money

- Field: `InsuranceRules`
- Values: `offered`, `payout`, `max_bet_fraction`
- Default: disabled, `2:1` payout, maximum half of the current main bet
- Effect: insurance is offered only when the dealer upcard is an ace. The
  insurance result is stored separately from main-hand settlements and is added
  to round net result. `EvenMoneyInsuranceStrategy` takes insurance only when
  the player has a natural blackjack.

## Dealer Peek

- Field: `DealerRules.peeks_for_blackjack`
- Values: `true`, `false`
- Default: `true`
- Effect: when enabled, dealer blackjack with an ace or ten-value upcard ends
  the round before player actions after any applicable insurance decision.

## European No Hole Card

- Field: `HoleCardRules.mode`
- Values: `american`, `european_no_hole_card`
- Default: `american`
- Effect: in `european_no_hole_card`, dealer starts with only the upcard. The
  second dealer card is drawn after player actions and before dealer play.

## ENHC Loss Rule

- Field: `HoleCardRules.enhc_loss_rule`
- Values: `all_bets`, `original_bet_only`
- Default: `all_bets`
- Effect: if the dealer blackjack appears after player actions in ENHC,
  `all_bets` loses current hand bets including double and split wagers.
  `original_bet_only` loses only one original wager for the round and returns
  additional wagers as zero-net settlements.

## Betting Systems

- Fields: betting strategy objects passed to `run_simulation`
- Values: flat, Martingale, Paroli, Fibonacci, D'Alembert
- Default: flat betting from `SimulationConfig.betting_amount`
- Effect: the betting strategy selects the initial wager once per round and is
  updated once after the round net result. Split hands do not update the betting
  system separately.

## Table Limits and Bankroll

- Field: `TableLimits`
- Values: positive minimum, maximum greater than or equal to minimum
- Effect: requested bets are clamped to table minimum and maximum. If bankroll
  is below table minimum or below an unclamped requested bet, the strategy raises
  `InsufficientBankrollError`.

## Hi-Lo Counting

- Field: optional `card_counter` passed to `play_round` or `run_simulation`
- Values: `HiLoCounter`
- Default: no counting
- Effect: revealed cards update running count. True count is calculated from the
  current running count and remaining cards. In American hole-card games, the
  dealer hole card updates the count only when revealed by peek, settlement, or
  dealer play. The count resets when the shoe resets after shuffle.

## Count-Based Insurance and Betting Spread

- Fields: `CountBasedInsuranceStrategy`, `TrueCountSpreadBettingStrategy`
- Effect: insurance can be taken only when true count reaches a configured
  threshold. Betting spread chooses the initial round wager from true-count
  thresholds while still respecting table limits and bankroll checks.

## Statistics and Reports

- Fields: `StatisticsCollector`, `SimulationReport`
- Values: streaming round aggregation
- Default: no collector unless passed to `run_simulation`
- Effect: statistics aggregate rounds without retaining every round inside the
  collector. Metrics include Welford mean/variance, house edge against initial
  bets and total action, RTP, max drawdown, and win/loss/push streaks. Reports
  can be rendered as JSON, CSV, or plain console text.

## YAML Configuration and CLI

- Fields: `simulation`, `bankroll`, `rules`, `player`, `output`
- Commands: `validate`, `run`, `trace`
- Overrides: `--rounds`, `--seed`
- Effect: YAML is converted into typed domain configuration before the engine is
  called. The CLI does not implement game behavior directly.

## Worker Simulation

- Fields: `WorkerShoeConfig`, `run_worker_simulations`
- Values: top-level seed, positive worker count, per-worker strategy factories
- Effect: rounds are split deterministically across workers. Each worker gets a
  derived seed and its own shoe, strategies, and statistics collector. Worker
  collectors are merged in worker-index order to avoid nondeterministic
  aggregation from process completion order.

## MVP Example Configurations

- `standard_6_deck_s17.yaml`: six-deck S17 American hole-card baseline.
- `standard_6_deck_h17.yaml`: six-deck H17 American hole-card variant.
- `blackjack_6_to_5.yaml`: H17 game with 6:5 blackjack payout.
- `european_no_hole_card.yaml`: ENHC with original-bet-only dealer blackjack
  loss handling.
- `validation_1m.yaml`: deterministic million-round validation profile using
  four workers.

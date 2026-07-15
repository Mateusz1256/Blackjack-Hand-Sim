# Blackjack Simulator

Blackjack Simulator is an open source engine for deterministic, configurable
blackjack simulations.

This project is a simulation and education tool. It does not guarantee profit
and is not financial advice or an encouragement to gamble.

## Goals

- Model blackjack rules precisely and testably.
- Keep domain logic independent from CLI, reports, and future web UI.
- Support deterministic simulations for a fixed seed.
- Make table rules, insurance strategies, and betting systems extensible.
- Scale from single traceable rounds to large statistical simulations.

## Planned Features

- Configurable deck count, penetration, S17/H17, peek, ENHC, surrender, double,
  split, insurance, and blackjack payout rules.
- Basic strategy profiles matched to table rules.
- Flat betting plus progressive systems such as Martingale, Paroli, Fibonacci,
  and D'Alembert.
- Streaming statistics, JSON/CSV export, CLI, and deterministic worker runs.

## Requirements

- Python 3.12 or newer.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quick Start

The package exposes cards, hands, shoe/dealer rules, hole-card models, double,
split, surrender, insurance, basic strategy, settlement, flat/progressive
betting, Hi-Lo counting, streaming statistics, report output, CLI, and worker
simulation primitives.

```python
import random
from decimal import Decimal

from blackjack_simulator import (
    Action,
    Card,
    DealerRules,
    Hand,
    Rank,
    Shoe,
    SimulationConfig,
    basic_strategy_for_rules,
    run_simulation,
)

hand = Hand(cards=[Card(Rank.ACE), Card(Rank.KING)])
print(hand.value)
print(hand.is_blackjack())

shoe = Shoe(decks=6, penetration=0.75, rng=random.Random(123))
config = SimulationConfig(
    rounds=10,
    initial_bankroll=Decimal("1000"),
    betting_amount=Decimal("10"),
    dealer_rules=DealerRules(hits_soft_17=False),
)
result = run_simulation(
    shoe=shoe,
    config=config,
    player_strategy=basic_strategy_for_rules(config.dealer_rules),
)
print(result.final_bankroll)
```

## Configuration Example

The CLI accepts YAML configuration such as
`configs/standard_6_deck_s17.yaml`. Additional examples cover H17, 6:5
blackjack payout, European no-hole-card, and a million-round validation run.

```yaml
simulation:
  rounds: 1000000
  seed: 123456

rules:
  decks: 6
  blackjack_payout: 1.5
  dealer:
    hits_soft_17: false
```

Betting strategy options:

```yaml
player:
  betting_strategy:
    type: flat
    amount: 10
```

Supported `type` values are `flat`, `martingale`, `paroli`, `fibonacci`,
`dalembert`, and `true_count_spread`. Progressive strategies use `amount` or
`base_amount`; `paroli` also accepts `max_wins`. Any strategy can define table
limits:

```yaml
table_limits:
  minimum: 10
  maximum: 500
```

For true-count betting:

```yaml
player:
  betting_strategy:
    type: true_count_spread
    amount: 10
    spread:
      0: 1
      2: 2
      4: 4
```

## CLI

```powershell
blackjack-simulator validate configs/standard_6_deck_s17.yaml
blackjack-simulator run configs/standard_6_deck_s17.yaml --rounds 100
blackjack-simulator trace configs/standard_6_deck_s17.yaml --rounds 1
blackjack-simulator trace configs/standard_6_deck_s17.yaml --rounds 1 --json-file trace.json
blackjack-simulator trace configs/standard_6_deck_s17.yaml --event-type card_dealt
blackjack-simulator audit configs/standard_6_deck_s17.yaml --rounds 100
blackjack-simulator audit configs/standard_6_deck_s17.yaml --rounds 10 --strict
blackjack-simulator compare configs/standard_6_deck_s17.yaml configs/blackjack_6_to_5.yaml --rounds 10000
blackjack-simulator batch configs/standard_6_deck_s17.yaml --sessions 100 --rounds-per-session 1000 --base-seed 42
blackjack-simulator presets list
blackjack-simulator presets export standard-6d-s17 standard-6d-s17.yaml
blackjack-simulator run configs/validation_1m.yaml
```

## Reports and Workers

Reports include streaming aggregates such as RTP, house edge, drawdown,
streaks, and variance. `run_worker_simulations` can split simulations across
deterministically seeded workers and merge their statistics without sharing
mutable simulation state.

Batch simulations run independent sessions from a deterministic base seed and
report final-bankroll distribution, risk of ruin, profit/loss rates, drawdown
percentiles, and per-session CSV/JSON output.

Built-in presets provide validated generic table-rule configurations with
metadata. They are read-only templates and avoid claims about specific casino
tables; export one to YAML before editing it as a custom configuration.

## Tests

```powershell
pytest
ruff check .
ruff format --check .
mypy src
```

## Roadmap

Implementation is split into task files under `tasks/`. Each task should be
completed, tested, and reviewed before the next major task starts.

## Contributing

Read `AGENTS.md` before changing the code. Keep commits small, deterministic,
and covered by tests.

## Credits

Created by Blackjack Simulator contributors.

## License

MIT. See `LICENSE`.

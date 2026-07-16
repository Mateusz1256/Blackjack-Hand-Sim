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
`dalembert`, `true_count_spread`, `bankroll_percentage`, and `kelly`.
Progressive strategies use `amount` or `base_amount`; `paroli` also accepts
`max_wins`. Any strategy can define table limits:

```yaml
table_limits:
  minimum: 10
  maximum: 500
```

Advanced bet sizing supports explicit rounding:

```yaml
bankroll:
  initial: 1000
  stop_loss: 250
  stop_win: 500

player:
  betting_strategy:
    type: bankroll_percentage
    percentage: 0.025
    rounding:
      mode: floor
      increment: 5
```

`kelly` sizing uses user-supplied assumptions (`edge`, `variance`, `fraction`);
it is an analytical sizing rule, not a recommendation.

For true-count betting:

```yaml
counting:
  enabled: true
  system: hi_lo
  true_count_rounding: floor
  min_remaining_decks: 1
  initial_running_count: 0

player:
  betting_strategy:
    type: true_count_spread
    amount: 10
    spread:
      0: 1
      2: 2
      4: 4
```

Supported counting systems are `hi_lo`, `ko`, `hi_opt_i`, `hi_opt_ii`, and
`omega_ii`. True-count rounding can be `none`, `floor`, `truncate`, or
`nearest`; `min_remaining_decks` prevents extreme division near the end of a
shoe.

Count-based deviations can wrap basic strategy:

```yaml
deviations:
  enabled: true
  sets:
    - illustrious_18
    - fab_4
  custom:
    - id: stand-16-vs-10
      hand_type: hard
      player_total: 16
      dealer_upcard: 10
      true_count_min: 0
      action: stand
      priority: 100
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

## Backend API

Task-oriented API work starts in `backend/src/blackjack_api`. The foundation
exposes a FastAPI app factory and a versioned health endpoint:

```powershell
uvicorn blackjack_api.main:app --reload
```

Health check: `GET /api/v1/health`. OpenAPI schema: `GET /openapi.json`.

The backend uses local SQLite persistence by default. Override the database
path with `BLACKJACK_API_DATABASE_PATH`; repositories store full configuration
snapshots so run metadata can be reproduced later.

Long-running backend work is routed through a local task queue abstraction with
bounded progress and cancellation support. Production Redis/distributed workers
are intentionally left for later deployment tasks.

Simulation endpoints are available under `/api/v1/simulations`: validate a
configuration, enqueue a run, poll status, cancel a job, and fetch completed
results or trace events.

Comparison and batch workflows are also asynchronous. Use `/api/v1/comparisons`
or `/api/v1/batches` to enqueue work, poll job status, retrieve completed
reports, and export JSON or CSV.

## Frontend

The frontend foundation lives in `frontend/` and uses Vite, React, TypeScript,
React Router, Vitest, and Testing Library.

```powershell
cd frontend
npm install
npm run dev
npm test
npm run build
```

Set `VITE_API_BASE_URL` when the API is not available through the default
`/api/v1` path or the Vite development proxy.

The configuration builder is available at `/configuration`. It covers engine
configuration fields, dynamic betting-strategy options, warning summaries,
generated YAML, and backend validation through `/api/v1/simulations/validate`.
It can also import YAML or JSON from pasted text or files, report unknown
fields before apply, preview config diffs, and export full or changed-only
configurations.

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

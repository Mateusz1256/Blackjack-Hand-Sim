# Blackjack Simulator

Blackjack Simulator is a planned open source engine for deterministic,
configurable blackjack simulations. The project currently includes the project
foundation plus the first domain primitives for cards and hands.

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
- Streaming statistics, JSON/CSV export, and a CLI.

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

At this stage the package exposes card, hand, shoe, and dealer-rule primitives.

```python
import random

from blackjack_simulator import Card, DealerRules, Hand, Rank, Shoe

hand = Hand(cards=[Card(Rank.ACE), Card(Rank.KING)])
print(hand.value)
print(hand.is_blackjack())

shoe = Shoe(decks=6, penetration=0.75, rng=random.Random(123))
print(shoe.draw())
print(DealerRules(hits_soft_17=False))
```

## Configuration Example

The final CLI will accept YAML configuration. The full schema will be introduced
in later tasks.

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

## CLI

The CLI is planned for a later task. No command-line entry point is shipped in
the current foundation step.

## Reports

Reports are planned to include bankroll history, expected value, RTP, house
edge, drawdown, streaks, and confidence intervals. They are not implemented in
this step.

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

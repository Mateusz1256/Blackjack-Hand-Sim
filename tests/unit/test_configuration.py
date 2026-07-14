from decimal import Decimal

import pytest

from blackjack_simulator.configuration import (
    ConfigurationError,
    load_app_config,
    parse_app_config,
)
from blackjack_simulator.rules import HoleCardMode, SurrenderType


def valid_config_text() -> str:
    return """
simulation:
  rounds: 3
  seed: 123
  workers: 1
bankroll:
  initial: 100
player:
  betting_strategy:
    type: flat
    amount: 10
  playing_strategy:
    type: basic_strategy
  insurance_strategy:
    type: never
rules:
  decks: 1
  penetration: 0.75
  blackjack_payout: 1.5
  dealer:
    hits_soft_17: false
    peeks_for_blackjack: true
  double:
    allowed: true
    after_split: true
    allowed_totals: [9, 10, 11]
  surrender:
    type: late
  split:
    allowed: true
    max_hands: 4
  insurance:
    offered: true
  hole_card:
    mode: american
output:
  console: true
"""


def test_parse_valid_app_config() -> None:
    config = parse_app_config(valid_config_text())

    assert config.simulation.rounds == 3
    assert config.simulation.seed == 123
    assert config.simulation.workers == 1
    assert config.engine_config.initial_bankroll == Decimal("100")
    assert config.engine_config.betting_amount == Decimal("10")
    assert config.engine_config.surrender_rules.surrender_type is SurrenderType.LATE
    assert config.engine_config.hole_card_rules.mode is HoleCardMode.AMERICAN


def test_parse_config_applies_overrides() -> None:
    config = parse_app_config(
        valid_config_text(),
        overrides={"rounds": 5, "seed": 999, "workers": 2},
    )

    assert config.simulation.rounds == 5
    assert config.simulation.seed == 999
    assert config.simulation.workers == 2


def test_invalid_config_raises_clear_error() -> None:
    with pytest.raises(ConfigurationError, match=r"simulation\.rounds"):
        parse_app_config("simulation:\n  rounds: 0\n")


def test_load_app_config_from_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "config.yaml"
    path.write_text(valid_config_text(), encoding="utf-8")

    config = load_app_config(path)

    assert config.simulation.rounds == 3

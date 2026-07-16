from decimal import Decimal

import pytest

from blackjack_simulator.betting import (
    BankrollPercentageBettingStrategy,
    DAlembertBettingStrategy,
    FibonacciBettingStrategy,
    FlatBettingStrategy,
    KellyStyleBettingStrategy,
    MartingaleBettingStrategy,
    ParoliBettingStrategy,
    TrueCountSpreadBettingStrategy,
)
from blackjack_simulator.configuration import (
    ConfigurationError,
    load_app_config,
    parse_app_config,
)
from blackjack_simulator.counting.system import (
    ConfigurableCardCounter,
    TrueCountRounding,
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


@pytest.mark.parametrize(
    ("strategy_type", "expected_type"),
    [
        ("flat", FlatBettingStrategy),
        ("martingale", MartingaleBettingStrategy),
        ("paroli", ParoliBettingStrategy),
        ("fibonacci", FibonacciBettingStrategy),
        ("dalembert", DAlembertBettingStrategy),
    ],
)
def test_parse_config_creates_progressive_betting_strategies(
    strategy_type: str,
    expected_type: type[object],
) -> None:
    text = valid_config_text().replace("type: flat", f"type: {strategy_type}")
    config = parse_app_config(text)
    shoe = config.create_shoe()

    strategy = config.create_betting_strategy(shoe, config.create_card_counter())

    assert isinstance(strategy, expected_type)
    assert strategy.next_bet(Decimal("100")) == Decimal("10")


def test_parse_config_creates_paroli_with_table_limits() -> None:
    text = valid_config_text().replace(
        "amount: 10",
        "amount: 5\n"
        "    max_wins: 2\n"
        "    table_limits:\n"
        "      minimum: 10\n"
        "      maximum: 25",
    )
    text = text.replace("type: flat", "type: paroli")
    config = parse_app_config(text)
    shoe = config.create_shoe()

    strategy = config.create_betting_strategy(shoe, config.create_card_counter())

    assert isinstance(strategy, ParoliBettingStrategy)
    assert strategy.next_bet(Decimal("100")) == Decimal("10")


def test_parse_config_creates_true_count_spread_betting_strategy() -> None:
    text = valid_config_text().replace(
        "type: flat\n    amount: 10",
        "type: true_count_spread\n    amount: 10\n    spread:\n      0: 1\n      2: 4",
    )
    config = parse_app_config(text)
    shoe = config.create_shoe()
    card_counter = config.create_card_counter()

    strategy = config.create_betting_strategy(shoe, card_counter)

    assert card_counter is not None
    assert isinstance(strategy, TrueCountSpreadBettingStrategy)
    assert strategy.next_bet(Decimal("100")) == Decimal("10")


def test_parse_config_creates_advanced_betting_strategies() -> None:
    percentage_text = valid_config_text().replace(
        "type: flat\n    amount: 10",
        "type: bankroll_percentage\n"
        "    amount: 10\n"
        "    percentage: 0.025\n"
        "    rounding:\n"
        "      mode: floor\n"
        "      increment: 5",
    )
    percentage_config = parse_app_config(percentage_text)
    percentage_strategy = percentage_config.create_betting_strategy(
        percentage_config.create_shoe(),
    )

    kelly_text = valid_config_text().replace(
        "type: flat\n    amount: 10",
        "type: kelly\n"
        "    amount: 10\n"
        "    edge: 0.02\n"
        "    variance: 1\n"
        "    fraction: 0.5\n"
        "    rounding:\n"
        "      mode: floor\n"
        "      increment: 1",
    )
    kelly_config = parse_app_config(kelly_text)
    kelly_strategy = kelly_config.create_betting_strategy(kelly_config.create_shoe())

    assert isinstance(percentage_strategy, BankrollPercentageBettingStrategy)
    assert percentage_strategy.next_bet(Decimal("1000")) == Decimal("25")
    assert isinstance(kelly_strategy, KellyStyleBettingStrategy)
    assert kelly_strategy.next_bet(Decimal("1000")) == Decimal("10")


def test_parse_config_creates_configured_card_counter() -> None:
    text = (
        valid_config_text()
        + """
counting:
  enabled: true
  system: omega_ii
  true_count_rounding: floor
  min_remaining_decks: 1
  initial_running_count: -4
  wonging:
    enter_at_true_count: 1
"""
    )
    config = parse_app_config(text)
    card_counter = config.create_card_counter()

    assert config.counting.enabled is True
    assert config.counting.system == "omega_ii"
    assert config.counting.true_count_rounding is TrueCountRounding.FLOOR
    assert config.counting.min_remaining_decks == Decimal("1")
    assert isinstance(card_counter, ConfigurableCardCounter)
    assert card_counter.system.name == "omega_ii"
    assert card_counter.running_count == -4


def test_parse_config_creates_deviating_strategy() -> None:
    text = (
        valid_config_text()
        + """
counting:
  enabled: true
deviations:
  enabled: true
  sets:
    - illustrious_18
  custom:
    - id: stand-12-vs-4
      hand_type: hard
      player_total: 12
      dealer_upcard: 4
      true_count_min: 1
      action: stand
      priority: 200
"""
    )
    config = parse_app_config(text)
    shoe = config.create_shoe()
    card_counter = config.create_card_counter()
    strategy = config.create_playing_strategy(shoe, card_counter)

    assert config.deviations.enabled is True
    assert config.deviations.sets == ("illustrious_18",)
    assert len(config.deviations.custom) == 1
    assert strategy.__class__.__name__ == "DeviatingStrategy"


def test_invalid_config_raises_clear_error() -> None:
    with pytest.raises(ConfigurationError, match=r"simulation\.rounds"):
        parse_app_config("simulation:\n  rounds: 0\n")


def test_load_app_config_from_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "config.yaml"
    path.write_text(valid_config_text(), encoding="utf-8")

    config = load_app_config(path)

    assert config.simulation.rounds == 3

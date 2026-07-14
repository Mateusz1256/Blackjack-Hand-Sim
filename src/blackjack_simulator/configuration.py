"""YAML configuration loading and validation."""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from pathlib import Path
from random import Random
from typing import Any

import yaml

from blackjack_simulator.betting import FlatBettingStrategy
from blackjack_simulator.betting.base import BettingStrategy
from blackjack_simulator.engine import (
    FlatBettingStrategyFactory,
    SimulationConfig,
    WorkerShoeConfig,
)
from blackjack_simulator.exceptions import BlackjackSimulatorError
from blackjack_simulator.rules import (
    DealerRules,
    DoubleRules,
    EnhcLossRule,
    HoleCardMode,
    HoleCardRules,
    InsuranceRules,
    SplitRules,
    SurrenderRules,
    SurrenderType,
)
from blackjack_simulator.shoe import Shoe
from blackjack_simulator.strategies import (
    AlwaysInsuranceStrategy,
    BasicStrategy,
    EvenMoneyInsuranceStrategy,
    NeverInsuranceStrategy,
    basic_strategy_for_rules,
)
from blackjack_simulator.strategies.insurance import InsuranceStrategy


class ConfigurationError(BlackjackSimulatorError):
    """Raised when configuration cannot be parsed or validated."""


@dataclass(frozen=True, slots=True)
class SimulationSettings:
    rounds: int
    seed: int
    workers: int = 1


@dataclass(frozen=True, slots=True)
class ShoeSettings:
    decks: int
    penetration: float
    shuffle_after_each_round: bool


@dataclass(frozen=True, slots=True)
class OutputSettings:
    console: bool = True
    json_file: str | None = None
    csv_file: str | None = None


@dataclass(frozen=True, slots=True)
class AppConfig:
    simulation: SimulationSettings
    shoe: ShoeSettings
    engine_config: SimulationConfig
    output: OutputSettings
    insurance_strategy_type: str = "never"

    def create_shoe(self) -> Shoe:
        return Shoe(
            decks=self.shoe.decks,
            penetration=self.shoe.penetration,
            rng=Random(self.simulation.seed),
            shuffle_after_each_round=self.shoe.shuffle_after_each_round,
        )

    def create_playing_strategy(self) -> BasicStrategy:
        return basic_strategy_for_rules(self.engine_config.dealer_rules)

    def create_playing_strategy_factory(self) -> Callable[[], BasicStrategy]:
        return partial(basic_strategy_for_rules, self.engine_config.dealer_rules)

    def create_insurance_strategy(self) -> InsuranceStrategy:
        if self.insurance_strategy_type == "always":
            return AlwaysInsuranceStrategy()
        if self.insurance_strategy_type == "even_money":
            return EvenMoneyInsuranceStrategy()
        if self.insurance_strategy_type == "count_based":
            msg = (
                "count_based insurance requires a counter "
                "and is not supported by config yet"
            )
            raise ConfigurationError(msg)
        if self.insurance_strategy_type == "never":
            return NeverInsuranceStrategy()

        msg = f"unsupported insurance strategy: {self.insurance_strategy_type}"
        raise ConfigurationError(msg)

    def create_betting_strategy(self) -> BettingStrategy:
        return FlatBettingStrategy(self.engine_config.betting_amount)

    def create_insurance_strategy_factory(
        self,
    ) -> Callable[[], InsuranceStrategy]:
        if self.insurance_strategy_type == "always":
            return AlwaysInsuranceStrategy
        if self.insurance_strategy_type == "even_money":
            return EvenMoneyInsuranceStrategy
        if self.insurance_strategy_type == "never":
            return NeverInsuranceStrategy

        self.create_insurance_strategy()
        return NeverInsuranceStrategy

    def create_betting_strategy_factory(self) -> Callable[[], BettingStrategy]:
        return FlatBettingStrategyFactory(self.engine_config.betting_amount)

    def create_worker_shoe_config(self) -> WorkerShoeConfig:
        return WorkerShoeConfig(
            decks=self.shoe.decks,
            penetration=self.shoe.penetration,
            shuffle_after_each_round=self.shoe.shuffle_after_each_round,
        )


def load_app_config(
    path: str | Path,
    *,
    overrides: dict[str, int] | None = None,
) -> AppConfig:
    return parse_app_config(Path(path).read_text(encoding="utf-8"), overrides=overrides)


def parse_app_config(
    text: str,
    *,
    overrides: dict[str, int] | None = None,
) -> AppConfig:
    try:
        raw = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        msg = f"invalid YAML: {exc}"
        raise ConfigurationError(msg) from exc
    if not isinstance(raw, dict):
        msg = "configuration root must be a mapping"
        raise ConfigurationError(msg)

    overrides = overrides or {}
    simulation = _parse_simulation(raw.get("simulation", {}), overrides)
    bankroll = _mapping(raw.get("bankroll", {}), "bankroll")
    player = _mapping(raw.get("player", {}), "player")
    rules = _mapping(raw.get("rules", {}), "rules")
    output = _parse_output(raw.get("output", {}))

    betting = _mapping(player.get("betting_strategy", {}), "player.betting_strategy")
    betting_type = str(betting.get("type", "flat"))
    if betting_type != "flat":
        msg = f"unsupported player.betting_strategy.type: {betting_type}"
        raise ConfigurationError(msg)

    dealer_rules = _parse_dealer_rules(rules.get("dealer", {}))
    engine_config = SimulationConfig(
        rounds=simulation.rounds,
        initial_bankroll=_decimal(bankroll.get("initial", "1000"), "bankroll.initial"),
        betting_amount=_decimal(
            betting.get("amount", "10"),
            "player.betting_strategy.amount",
        ),
        blackjack_payout=_decimal(
            rules.get("blackjack_payout", "1.5"),
            "rules.blackjack_payout",
        ),
        dealer_rules=dealer_rules,
        double_rules=_parse_double_rules(rules.get("double", {})),
        surrender_rules=_parse_surrender_rules(rules.get("surrender", {})),
        split_rules=_parse_split_rules(rules.get("split", {})),
        insurance_rules=_parse_insurance_rules(rules.get("insurance", {})),
        hole_card_rules=_parse_hole_card_rules(rules.get("hole_card", {})),
    )

    return AppConfig(
        simulation=simulation,
        shoe=ShoeSettings(
            decks=_positive_int(rules.get("decks", 6), "rules.decks"),
            penetration=_float_between(
                rules.get("penetration", 0.75),
                "rules.penetration",
                lower_exclusive=0,
                upper_inclusive=1,
            ),
            shuffle_after_each_round=bool(rules.get("shuffle_after_each_round", False)),
        ),
        engine_config=engine_config,
        output=output,
        insurance_strategy_type=str(
            _mapping(
                player.get("insurance_strategy", {}),
                "player.insurance_strategy",
            ).get(
                "type",
                "never",
            ),
        ),
    )


def _parse_simulation(raw: object, overrides: dict[str, int]) -> SimulationSettings:
    data = _mapping(raw, "simulation")
    rounds = overrides.get("rounds", data.get("rounds", 1))
    seed = overrides.get("seed", data.get("seed", 1))
    workers = overrides.get("workers", data.get("workers", 1))
    return SimulationSettings(
        rounds=_positive_int(rounds, "simulation.rounds"),
        seed=_int(seed, "simulation.seed"),
        workers=_positive_int(workers, "simulation.workers"),
    )


def _parse_output(raw: object) -> OutputSettings:
    data = _mapping(raw, "output")
    return OutputSettings(
        console=bool(data.get("console", True)),
        json_file=_optional_str(data.get("json_file")),
        csv_file=_optional_str(data.get("csv_file")),
    )


def _parse_dealer_rules(raw: object) -> DealerRules:
    data = _mapping(raw, "rules.dealer")
    return DealerRules(
        hits_soft_17=bool(data.get("hits_soft_17", False)),
        peeks_for_blackjack=bool(data.get("peeks_for_blackjack", True)),
    )


def _parse_double_rules(raw: object) -> DoubleRules:
    data = _mapping(raw, "rules.double")
    totals = data.get("allowed_totals")
    return DoubleRules(
        allowed=bool(data.get("allowed", False)),
        after_split=bool(data.get("after_split", False)),
        allowed_totals=(
            frozenset(_int(value, "rules.double.allowed_totals") for value in totals)
            if totals is not None
            else None
        ),
    )


def _parse_surrender_rules(raw: object) -> SurrenderRules:
    data = _mapping(raw, "rules.surrender")
    return SurrenderRules(
        surrender_type=SurrenderType(str(data.get("type", SurrenderType.NONE.value))),
    )


def _parse_split_rules(raw: object) -> SplitRules:
    data = _mapping(raw, "rules.split")
    return SplitRules(
        allowed=bool(data.get("allowed", False)),
        max_hands=_positive_int(data.get("max_hands", 4), "rules.split.max_hands"),
        require_same_rank=bool(data.get("require_same_rank", True)),
        resplit_aces=bool(data.get("resplit_aces", False)),
        hit_split_aces=bool(data.get("hit_split_aces", False)),
        double_after_split_aces=bool(data.get("double_after_split_aces", False)),
        blackjack_after_split_counts_as_blackjack=bool(
            data.get("blackjack_after_split_counts_as_blackjack", False),
        ),
    )


def _parse_insurance_rules(raw: object) -> InsuranceRules:
    data = _mapping(raw, "rules.insurance")
    return InsuranceRules(
        offered=bool(data.get("offered", False)),
        payout=_decimal(data.get("payout", "2"), "rules.insurance.payout"),
        max_bet_fraction=_decimal(
            data.get("max_bet_fraction", "0.5"),
            "rules.insurance.max_bet_fraction",
        ),
    )


def _parse_hole_card_rules(raw: object) -> HoleCardRules:
    data = _mapping(raw, "rules.hole_card")
    return HoleCardRules(
        mode=HoleCardMode(str(data.get("mode", HoleCardMode.AMERICAN.value))),
        enhc_loss_rule=EnhcLossRule(
            str(data.get("enhc_loss_rule", EnhcLossRule.ALL_BETS.value)),
        ),
    )


def _mapping(value: object, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = f"{field_name} must be a mapping"
        raise ConfigurationError(msg)
    return value


def _positive_int(value: object, field_name: str) -> int:
    parsed = _int(value, field_name)
    if parsed <= 0:
        msg = f"{field_name} must be positive"
        raise ConfigurationError(msg)
    return parsed


def _int(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        msg = f"{field_name} must be an integer"
        raise ConfigurationError(msg)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError as exc:
            msg = f"{field_name} must be an integer"
            raise ConfigurationError(msg) from exc
    if not isinstance(value, float):
        msg = f"{field_name} must be an integer"
        raise ConfigurationError(msg)
    if not value.is_integer():
        msg = f"{field_name} must be an integer"
        raise ConfigurationError(msg)
    return int(value)


def _decimal(value: object, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:
        msg = f"{field_name} must be decimal-compatible"
        raise ConfigurationError(msg) from exc


def _float_between(
    value: object,
    field_name: str,
    *,
    lower_exclusive: float,
    upper_inclusive: float,
) -> float:
    if isinstance(value, bool):
        msg = f"{field_name} must be numeric"
        raise ConfigurationError(msg)
    try:
        parsed = float(value) if isinstance(value, (int, float, str)) else None
    except (TypeError, ValueError) as exc:
        msg = f"{field_name} must be numeric"
        raise ConfigurationError(msg) from exc
    if parsed is None:
        msg = f"{field_name} must be numeric"
        raise ConfigurationError(msg)
    if not lower_exclusive < parsed <= upper_inclusive:
        msg = f"{field_name} must be > {lower_exclusive} and <= {upper_inclusive}"
        raise ConfigurationError(msg)
    return parsed


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)

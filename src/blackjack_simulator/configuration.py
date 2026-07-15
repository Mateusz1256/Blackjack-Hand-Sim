"""YAML configuration loading and validation."""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from pathlib import Path
from random import Random
from typing import Any

import yaml

from blackjack_simulator.betting import (
    DAlembertBettingStrategy,
    FibonacciBettingStrategy,
    FlatBettingStrategy,
    MartingaleBettingStrategy,
    ParoliBettingStrategy,
    TableLimits,
    TrueCountSpreadBettingStrategy,
)
from blackjack_simulator.betting.base import BettingStrategy
from blackjack_simulator.counting.base import CardCounter
from blackjack_simulator.counting.system import (
    ConfigurableCardCounter,
    TrueCountRounding,
    get_counting_system,
)
from blackjack_simulator.engine import (
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
class BettingSettings:
    strategy_type: str
    base_amount: Decimal
    table_limits: TableLimits | None = None
    max_wins: int = 3
    spread: dict[Decimal, Decimal] | None = None


@dataclass(frozen=True, slots=True)
class CountingSettings:
    enabled: bool
    system: str = "hi_lo"
    true_count_rounding: TrueCountRounding = TrueCountRounding.NONE
    min_remaining_decks: Decimal = Decimal("0")
    initial_running_count: int | None = None
    wonging: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ConfiguredBettingStrategyFactory:
    settings: BettingSettings

    def __call__(
        self,
        shoe: Shoe,
        card_counter: CardCounter | None = None,
    ) -> BettingStrategy:
        strategy_type = self.settings.strategy_type
        if strategy_type == "flat":
            return FlatBettingStrategy(
                amount=self.settings.base_amount,
                table_limits=self.settings.table_limits,
            )
        if strategy_type == "martingale":
            return MartingaleBettingStrategy(
                base_amount=self.settings.base_amount,
                table_limits=self.settings.table_limits,
            )
        if strategy_type == "paroli":
            return ParoliBettingStrategy(
                base_amount=self.settings.base_amount,
                table_limits=self.settings.table_limits,
                max_wins=self.settings.max_wins,
            )
        if strategy_type == "fibonacci":
            return FibonacciBettingStrategy(
                base_amount=self.settings.base_amount,
                table_limits=self.settings.table_limits,
            )
        if strategy_type == "dalembert":
            return DAlembertBettingStrategy(
                base_amount=self.settings.base_amount,
                table_limits=self.settings.table_limits,
            )
        if strategy_type == "true_count_spread":
            if card_counter is None:
                msg = "true_count_spread betting requires a card counter"
                raise ConfigurationError(msg)
            return TrueCountSpreadBettingStrategy(
                counter=card_counter,
                base_amount=self.settings.base_amount,
                spread=self.settings.spread or {Decimal("0"): Decimal("1")},
                remaining_cards_provider=lambda: shoe.remaining_cards,
                table_limits=self.settings.table_limits,
            )

        msg = f"unsupported player.betting_strategy.type: {strategy_type}"
        raise ConfigurationError(msg)


@dataclass(frozen=True, slots=True)
class AppConfig:
    simulation: SimulationSettings
    shoe: ShoeSettings
    engine_config: SimulationConfig
    output: OutputSettings
    betting: BettingSettings
    counting: CountingSettings
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

    def create_card_counter(self) -> CardCounter | None:
        if self.counting.enabled or self.betting.strategy_type == "true_count_spread":
            return ConfigurableCardCounter(
                system=get_counting_system(self.counting.system),
                initial_running_count=self.counting.initial_running_count,
                true_count_rounding=self.counting.true_count_rounding,
                min_remaining_decks=self.counting.min_remaining_decks,
            )
        return None

    def create_card_counter_factory(self) -> Callable[[], CardCounter] | None:
        if self.counting.enabled or self.betting.strategy_type == "true_count_spread":
            settings = self.counting

            def factory() -> CardCounter:
                return ConfigurableCardCounter(
                    system=get_counting_system(settings.system),
                    initial_running_count=settings.initial_running_count,
                    true_count_rounding=settings.true_count_rounding,
                    min_remaining_decks=settings.min_remaining_decks,
                )

            return factory
        return None

    def create_betting_strategy(
        self,
        shoe: Shoe | None = None,
        card_counter: CardCounter | None = None,
    ) -> BettingStrategy:
        shoe = shoe or self.create_shoe()
        return ConfiguredBettingStrategyFactory(self.betting)(shoe, card_counter)

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

    def create_betting_strategy_factory(
        self,
    ) -> Callable[[Shoe, CardCounter | None], BettingStrategy]:
        return ConfiguredBettingStrategyFactory(self.betting)

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
    counting = _parse_counting_settings(raw.get("counting", {}))

    betting = _parse_betting_settings(
        player.get("betting_strategy", {}),
        bankroll,
    )

    dealer_rules = _parse_dealer_rules(rules.get("dealer", {}))
    engine_config = SimulationConfig(
        rounds=simulation.rounds,
        initial_bankroll=_decimal(bankroll.get("initial", "1000"), "bankroll.initial"),
        betting_amount=_decimal(
            betting.base_amount,
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
        betting=betting,
        counting=counting,
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


def _parse_counting_settings(raw: object) -> CountingSettings:
    data = _mapping(raw, "counting")
    system = _normalize_counting_system(str(data.get("system", "hi_lo")))
    try:
        get_counting_system(system)
    except ValueError as exc:
        raise ConfigurationError(str(exc)) from exc

    return CountingSettings(
        enabled=bool(data.get("enabled", False)),
        system=system,
        true_count_rounding=_parse_true_count_rounding(
            data.get("true_count_rounding", TrueCountRounding.NONE.value),
        ),
        min_remaining_decks=_non_negative_decimal(
            data.get("min_remaining_decks", "0"),
            "counting.min_remaining_decks",
        ),
        initial_running_count=(
            None
            if data.get("initial_running_count") is None
            else _int(
                data.get("initial_running_count"),
                "counting.initial_running_count",
            )
        ),
        wonging=_optional_mapping(data.get("wonging"), "counting.wonging"),
    )


def _parse_true_count_rounding(raw: object) -> TrueCountRounding:
    normalized = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    try:
        return TrueCountRounding(normalized)
    except ValueError as exc:
        msg = f"unsupported counting.true_count_rounding: {raw}"
        raise ConfigurationError(msg) from exc


def _parse_betting_settings(raw: object, bankroll: dict[str, Any]) -> BettingSettings:
    data = _mapping(raw, "player.betting_strategy")
    strategy_type = _normalize_betting_type(str(data.get("type", "flat")))
    supported = {
        "flat",
        "martingale",
        "paroli",
        "fibonacci",
        "dalembert",
        "true_count_spread",
    }
    if strategy_type not in supported:
        msg = f"unsupported player.betting_strategy.type: {data.get('type', 'flat')}"
        raise ConfigurationError(msg)

    amount = data.get("base_amount", data.get("amount", "10"))
    return BettingSettings(
        strategy_type=strategy_type,
        base_amount=_decimal(amount, "player.betting_strategy.amount"),
        table_limits=_parse_table_limits(data, bankroll),
        max_wins=_positive_int(
            data.get("max_wins", 3),
            "player.betting_strategy.max_wins",
        ),
        spread=_parse_spread(data.get("spread")),
    )


def _parse_table_limits(
    betting: dict[str, Any],
    bankroll: dict[str, Any],
) -> TableLimits | None:
    raw_limits = betting.get("table_limits")
    if raw_limits is not None:
        limits = _mapping(raw_limits, "player.betting_strategy.table_limits")
        return TableLimits(
            minimum=_decimal(
                limits.get("minimum", limits.get("min")),
                "player.betting_strategy.table_limits.minimum",
            ),
            maximum=_decimal(
                limits.get("maximum", limits.get("max")),
                "player.betting_strategy.table_limits.maximum",
            ),
        )

    minimum = bankroll.get("table_minimum")
    maximum = bankroll.get("table_maximum")
    if minimum is None and maximum is None:
        return None
    if minimum is None or maximum is None:
        msg = "bankroll table_minimum and table_maximum must be configured together"
        raise ConfigurationError(msg)
    return TableLimits(
        minimum=_decimal(minimum, "bankroll.table_minimum"),
        maximum=_decimal(maximum, "bankroll.table_maximum"),
    )


def _parse_spread(raw: object) -> dict[Decimal, Decimal] | None:
    if raw is None:
        return None
    data = _mapping(raw, "player.betting_strategy.spread")
    return {
        _decimal(threshold, "player.betting_strategy.spread.threshold"): _decimal(
            multiplier,
            "player.betting_strategy.spread.multiplier",
        )
        for threshold, multiplier in data.items()
    }


def _normalize_betting_type(raw: str) -> str:
    normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "d_alembert": "dalembert",
        "d'alembert": "dalembert",
        "true_count": "true_count_spread",
        "count_spread": "true_count_spread",
    }
    return aliases.get(normalized, normalized)


def _normalize_counting_system(raw: str) -> str:
    normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "hilo": "hi_lo",
        "hiopt_i": "hi_opt_i",
        "hiopt_1": "hi_opt_i",
        "hi_opt_1": "hi_opt_i",
        "hiopt_ii": "hi_opt_ii",
        "hiopt_2": "hi_opt_ii",
        "hi_opt_2": "hi_opt_ii",
        "omega2": "omega_ii",
        "omega_2": "omega_ii",
    }
    return aliases.get(normalized, normalized)


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


def _non_negative_decimal(value: object, field_name: str) -> Decimal:
    parsed = _decimal(value, field_name)
    if parsed < 0:
        msg = f"{field_name} must not be negative"
        raise ConfigurationError(msg)
    return parsed


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


def _optional_mapping(value: object, field_name: str) -> dict[str, Any] | None:
    if value is None:
        return None
    return _mapping(value, field_name)

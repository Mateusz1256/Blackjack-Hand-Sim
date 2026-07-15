"""Configurable card counting systems."""

from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_UP, Decimal
from enum import StrEnum

from blackjack_simulator.cards import Card, Rank


class TrueCountRounding(StrEnum):
    NONE = "none"
    FLOOR = "floor"
    TRUNCATE = "truncate"
    NEAREST = "nearest"


@dataclass(frozen=True, slots=True)
class CountingSystem:
    name: str
    values: dict[Rank, int]
    balanced: bool
    default_initial_running_count: int = 0

    def value_for(self, rank: Rank) -> int:
        return self.values[rank]


@dataclass(slots=True)
class ConfigurableCardCounter:
    system: CountingSystem
    initial_running_count: int | None = None
    true_count_rounding: TrueCountRounding = TrueCountRounding.NONE
    min_remaining_decks: Decimal = Decimal("0")
    running_count: int = 0
    cards_seen: int = 0

    def __post_init__(self) -> None:
        if self.min_remaining_decks < 0:
            msg = "minimum remaining decks must not be negative"
            raise ValueError(msg)
        self.running_count = self._initial_count()

    def observe(self, card: Card) -> None:
        self.running_count += self.system.value_for(card.rank)
        self.cards_seen += 1

    def reset(self) -> None:
        self.running_count = self._initial_count()
        self.cards_seen = 0

    def true_count(self, *, remaining_cards: int) -> Decimal:
        if remaining_cards <= 0:
            raw = Decimal(self.running_count)
        else:
            remaining_decks = Decimal(remaining_cards) / Decimal(52)
            denominator = max(remaining_decks, self.min_remaining_decks)
            if denominator == 0:
                raw = Decimal(self.running_count)
            else:
                raw = Decimal(self.running_count) / denominator
        return round_true_count(raw, self.true_count_rounding)

    def _initial_count(self) -> int:
        if self.initial_running_count is not None:
            return self.initial_running_count
        return self.system.default_initial_running_count


def round_true_count(value: Decimal, mode: TrueCountRounding) -> Decimal:
    if mode is TrueCountRounding.NONE:
        return value
    if mode is TrueCountRounding.FLOOR:
        return value.to_integral_value(rounding=ROUND_FLOOR)
    if mode is TrueCountRounding.TRUNCATE:
        return value.to_integral_value(rounding=ROUND_DOWN)
    if mode is TrueCountRounding.NEAREST:
        return value.to_integral_value(rounding=ROUND_HALF_UP)
    return value


def get_counting_system(name: str) -> CountingSystem:
    normalized = _normalize_system_name(name)
    try:
        return COUNTING_SYSTEMS[normalized]
    except KeyError as exc:
        msg = f"unsupported counting system: {name}"
        raise ValueError(msg) from exc


def _normalize_system_name(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(" ", "_")


COUNTING_SYSTEMS: dict[str, CountingSystem] = {
    "hi_lo": CountingSystem(
        name="hi_lo",
        balanced=True,
        values={
            Rank.TWO: 1,
            Rank.THREE: 1,
            Rank.FOUR: 1,
            Rank.FIVE: 1,
            Rank.SIX: 1,
            Rank.SEVEN: 0,
            Rank.EIGHT: 0,
            Rank.NINE: 0,
            Rank.TEN: -1,
            Rank.JACK: -1,
            Rank.QUEEN: -1,
            Rank.KING: -1,
            Rank.ACE: -1,
        },
    ),
    "ko": CountingSystem(
        name="ko",
        balanced=False,
        values={
            Rank.TWO: 1,
            Rank.THREE: 1,
            Rank.FOUR: 1,
            Rank.FIVE: 1,
            Rank.SIX: 1,
            Rank.SEVEN: 1,
            Rank.EIGHT: 0,
            Rank.NINE: 0,
            Rank.TEN: -1,
            Rank.JACK: -1,
            Rank.QUEEN: -1,
            Rank.KING: -1,
            Rank.ACE: -1,
        },
    ),
    "hi_opt_i": CountingSystem(
        name="hi_opt_i",
        balanced=True,
        values={
            Rank.TWO: 0,
            Rank.THREE: 1,
            Rank.FOUR: 1,
            Rank.FIVE: 1,
            Rank.SIX: 1,
            Rank.SEVEN: 0,
            Rank.EIGHT: 0,
            Rank.NINE: 0,
            Rank.TEN: -1,
            Rank.JACK: -1,
            Rank.QUEEN: -1,
            Rank.KING: -1,
            Rank.ACE: 0,
        },
    ),
    "hi_opt_ii": CountingSystem(
        name="hi_opt_ii",
        balanced=True,
        values={
            Rank.TWO: 1,
            Rank.THREE: 1,
            Rank.FOUR: 2,
            Rank.FIVE: 2,
            Rank.SIX: 1,
            Rank.SEVEN: 1,
            Rank.EIGHT: 0,
            Rank.NINE: 0,
            Rank.TEN: -2,
            Rank.JACK: -2,
            Rank.QUEEN: -2,
            Rank.KING: -2,
            Rank.ACE: 0,
        },
    ),
    "omega_ii": CountingSystem(
        name="omega_ii",
        balanced=True,
        values={
            Rank.TWO: 1,
            Rank.THREE: 1,
            Rank.FOUR: 2,
            Rank.FIVE: 2,
            Rank.SIX: 2,
            Rank.SEVEN: 1,
            Rank.EIGHT: 0,
            Rank.NINE: -1,
            Rank.TEN: -2,
            Rank.JACK: -2,
            Rank.QUEEN: -2,
            Rank.KING: -2,
            Rank.ACE: 0,
        },
    ),
}

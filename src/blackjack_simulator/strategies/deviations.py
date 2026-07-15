"""Count-based deviations layered over basic strategy."""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank, card_value
from blackjack_simulator.counting.base import CardCounter
from blackjack_simulator.hand import Hand
from blackjack_simulator.strategies.basic_strategy import BasicStrategy


class DeviationHandType(StrEnum):
    HARD = "hard"
    SOFT = "soft"
    PAIR = "pair"
    ANY = "any"


@dataclass(frozen=True, slots=True)
class StrategyDeviation:
    id: str
    hand_type: DeviationHandType
    player_total: int | None
    dealer_upcard: int
    true_count_min: Decimal | None
    true_count_max: Decimal | None
    action: Action
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.id:
            msg = "deviation id must not be empty"
            raise ValueError(msg)
        if not 2 <= self.dealer_upcard <= 11:
            msg = "dealer upcard must be between 2 and 11"
            raise ValueError(msg)
        if self.true_count_min is None and self.true_count_max is None:
            msg = "deviation must define at least one count bound"
            raise ValueError(msg)
        if (
            self.true_count_min is not None
            and self.true_count_max is not None
            and self.true_count_min > self.true_count_max
        ):
            msg = "deviation true count min must not exceed max"
            raise ValueError(msg)

    def matches(
        self,
        hand: Hand,
        dealer_upcard: Card,
        true_count: Decimal,
    ) -> bool:
        if self.dealer_upcard != _dealer_value(dealer_upcard):
            return False
        if self.player_total is not None and self.player_total != hand.value:
            return False
        if not _hand_type_matches(hand, self.hand_type):
            return False
        if self.true_count_min is not None and true_count < self.true_count_min:
            return False
        return not (
            self.true_count_max is not None and true_count > self.true_count_max
        )


@dataclass(frozen=True, slots=True)
class DeviatingStrategy:
    base_strategy: BasicStrategy
    deviations: tuple[StrategyDeviation, ...]
    counter: CardCounter | None
    remaining_cards_provider: object

    def __post_init__(self) -> None:
        validate_deviation_conflicts(self.deviations)

    def choose_action(
        self,
        hand: Hand,
        dealer_upcard: Card,
        legal_actions: frozenset[Action] | None = None,
    ) -> Action:
        base_action = self.base_strategy.choose_action(
            hand,
            dealer_upcard,
            legal_actions,
        )
        if self.counter is None:
            return base_action

        true_count = self.counter.true_count(
            remaining_cards=_remaining_cards(self.remaining_cards_provider),
        )
        matching = [
            deviation
            for deviation in self.deviations
            if deviation.matches(hand, dealer_upcard, true_count)
        ]
        if not matching:
            return base_action

        deviation = max(matching, key=lambda item: item.priority)
        legal = legal_actions or self.base_strategy.legal_actions
        if deviation.action in legal:
            return deviation.action
        return self.base_strategy._to_legal_action(
            _action_to_decision(deviation.action),
            hand,
            dealer_upcard,
            legal,
        )


def validate_deviation_conflicts(
    deviations: Iterable[StrategyDeviation],
) -> None:
    by_key: dict[tuple[DeviationHandType, int | None, int, int], Action] = {}
    for deviation in deviations:
        key = (
            deviation.hand_type,
            deviation.player_total,
            deviation.dealer_upcard,
            deviation.priority,
        )
        existing = by_key.get(key)
        if existing is not None and existing is not deviation.action:
            msg = f"conflicting deviations for priority {deviation.priority}: {key}"
            raise ValueError(msg)
        by_key[key] = deviation.action


def get_builtin_deviations(name: str) -> tuple[StrategyDeviation, ...]:
    normalized = name.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized == "illustrious_18":
        return ILLUSTRIOUS_18
    if normalized == "fab_4":
        return FAB_4
    msg = f"unknown deviation set: {name}"
    raise ValueError(msg)


def _dealer_value(card: Card) -> int:
    if card.rank is Rank.ACE:
        return 11
    return min(card_value(card), 10)


def _hand_type_matches(hand: Hand, hand_type: DeviationHandType) -> bool:
    if hand_type is DeviationHandType.ANY:
        return True
    if hand_type is DeviationHandType.PAIR:
        return hand.is_pair()
    if hand_type is DeviationHandType.SOFT:
        return hand.is_soft
    return not hand.is_soft


def _remaining_cards(provider: object) -> int:
    remaining_cards = getattr(provider, "remaining_cards", None)
    if isinstance(remaining_cards, int):
        return remaining_cards
    return 0


def _action_to_decision(action: Action):  # type: ignore[no-untyped-def]
    from blackjack_simulator.strategies.basic_strategy_tables import StrategyDecision

    if action is Action.HIT:
        return StrategyDecision.HIT
    if action is Action.STAND:
        return StrategyDecision.STAND
    if action is Action.DOUBLE:
        return StrategyDecision.DOUBLE_HIT
    if action is Action.SURRENDER:
        return StrategyDecision.SURRENDER_HIT
    if action is Action.SPLIT:
        return StrategyDecision.SPLIT
    msg = f"unsupported deviation action: {action}"
    raise ValueError(msg)


def _hard(
    deviation_id: str,
    total: int,
    dealer: int,
    minimum: str,
    action: Action,
    priority: int,
) -> StrategyDeviation:
    return StrategyDeviation(
        id=deviation_id,
        hand_type=DeviationHandType.HARD,
        player_total=total,
        dealer_upcard=dealer,
        true_count_min=Decimal(minimum),
        true_count_max=None,
        action=action,
        priority=priority,
    )


def _hard_below(
    deviation_id: str,
    total: int,
    dealer: int,
    maximum: str,
    action: Action,
    priority: int,
) -> StrategyDeviation:
    return StrategyDeviation(
        id=deviation_id,
        hand_type=DeviationHandType.HARD,
        player_total=total,
        dealer_upcard=dealer,
        true_count_min=None,
        true_count_max=Decimal(maximum),
        action=action,
        priority=priority,
    )


ILLUSTRIOUS_18 = (
    _hard("insurance-ace", 16, 11, "3", Action.STAND, 100),
    _hard("16-vs-10-stand", 16, 10, "0", Action.STAND, 90),
    _hard("15-vs-10-stand", 15, 10, "4", Action.STAND, 80),
    _hard("10-vs-10-double", 10, 10, "4", Action.DOUBLE, 70),
    _hard("12-vs-3-stand", 12, 3, "2", Action.STAND, 60),
    _hard("12-vs-2-stand", 12, 2, "3", Action.STAND, 50),
    _hard("11-vs-ace-double", 11, 11, "1", Action.DOUBLE, 40),
    _hard("9-vs-2-double", 9, 2, "1", Action.DOUBLE, 30),
    _hard("10-vs-ace-double", 10, 11, "4", Action.DOUBLE, 20),
    _hard_below("13-vs-2-hit", 13, 2, "-1", Action.HIT, 10),
)

FAB_4 = (
    _hard("15-vs-10-surrender", 15, 10, "0", Action.SURRENDER, 100),
    _hard("15-vs-9-surrender", 15, 9, "2", Action.SURRENDER, 90),
    _hard("14-vs-10-surrender", 14, 10, "3", Action.SURRENDER, 80),
    _hard("14-vs-ace-surrender", 14, 11, "3", Action.SURRENDER, 70),
)

from decimal import Decimal

import pytest

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.counting import ConfigurableCardCounter, get_counting_system
from blackjack_simulator.hand import Hand
from blackjack_simulator.round import play_round
from blackjack_simulator.rules import DealerRules
from blackjack_simulator.strategies import BasicStrategy, BasicStrategyProfile
from blackjack_simulator.strategies.deviations import (
    DeviatingStrategy,
    DeviationHandType,
    StrategyDeviation,
    get_builtin_deviations,
    validate_deviation_conflicts,
)
from blackjack_simulator.trace import TraceCollector, TraceEventType


class StubShoe:
    def __init__(self, *ranks: Rank) -> None:
        self._cards = [Card(rank) for rank in ranks]

    def draw(self) -> Card:
        return self._cards.pop(0)

    @property
    def remaining_cards(self) -> int:
        return len(self._cards)

    @property
    def needs_shuffle(self) -> bool:
        return False

    def reset(self) -> None:
        return None


def hard_hand(*ranks: Rank) -> Hand:
    return Hand(cards=[Card(rank) for rank in ranks])


def test_builtin_illustrious_18_example_stands_on_16_vs_10() -> None:
    counter = ConfigurableCardCounter(
        system=get_counting_system("hi_lo"),
        initial_running_count=1,
    )
    strategy = DeviatingStrategy(
        base_strategy=BasicStrategy(BasicStrategyProfile.S17),
        deviations=get_builtin_deviations("illustrious_18"),
        counter=counter,
        remaining_cards_provider=type("Shoe", (), {"remaining_cards": 52})(),
    )

    action = strategy.choose_action(
        hard_hand(Rank.TEN, Rank.SIX),
        Card(Rank.TEN),
        frozenset({Action.HIT, Action.STAND}),
    )

    assert action is Action.STAND


def test_conflicting_deviations_at_same_priority_are_rejected() -> None:
    first = StrategyDeviation(
        id="first",
        hand_type=DeviationHandType.HARD,
        player_total=16,
        dealer_upcard=10,
        true_count_min=Decimal("0"),
        true_count_max=None,
        action=Action.STAND,
        priority=1,
    )
    second = StrategyDeviation(
        id="second",
        hand_type=DeviationHandType.HARD,
        player_total=16,
        dealer_upcard=10,
        true_count_min=Decimal("1"),
        true_count_max=None,
        action=Action.HIT,
        priority=1,
    )

    with pytest.raises(ValueError, match="conflicting deviations"):
        validate_deviation_conflicts([first, second])


def test_illegal_deviation_falls_back_to_legal_action() -> None:
    counter = ConfigurableCardCounter(
        system=get_counting_system("hi_lo"),
        initial_running_count=4,
    )
    strategy = DeviatingStrategy(
        base_strategy=BasicStrategy(BasicStrategyProfile.S17),
        deviations=(
            StrategyDeviation(
                id="double-16",
                hand_type=DeviationHandType.HARD,
                player_total=16,
                dealer_upcard=10,
                true_count_min=Decimal("0"),
                true_count_max=None,
                action=Action.DOUBLE,
            ),
        ),
        counter=counter,
        remaining_cards_provider=type("Shoe", (), {"remaining_cards": 52})(),
    )

    action = strategy.choose_action(
        hard_hand(Rank.TEN, Rank.SIX),
        Card(Rank.TEN),
        frozenset({Action.HIT, Action.STAND}),
    )

    assert action is Action.HIT


def test_deviation_affects_deterministic_round_trace() -> None:
    shoe = StubShoe(Rank.TEN, Rank.TEN, Rank.SIX, Rank.FIVE, Rank.TEN)
    counter = ConfigurableCardCounter(
        system=get_counting_system("hi_lo"),
        initial_running_count=2,
    )
    trace_collector = TraceCollector()
    strategy = DeviatingStrategy(
        base_strategy=BasicStrategy(BasicStrategyProfile.S17),
        deviations=get_builtin_deviations("illustrious_18"),
        counter=counter,
        remaining_cards_provider=shoe,
    )

    play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        player_strategy=strategy,
        bet=Decimal("10"),
        card_counter=counter,
        trace_collector=trace_collector,
    )

    resolved = [
        event
        for event in trace_collector.events
        if event.event_type is TraceEventType.STRATEGY_DECISION_RESOLVED
    ]
    assert resolved[0].details["executed_action"] == "stand"

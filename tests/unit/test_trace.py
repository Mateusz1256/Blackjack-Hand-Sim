from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.engine import SimulationConfig, run_simulation
from blackjack_simulator.round import FixedActionStrategy
from blackjack_simulator.rules import DealerRules
from blackjack_simulator.trace import TraceCollector, TraceEvent, TraceEventType


class ScriptedShoe:
    def __init__(self, *ranks: Rank) -> None:
        self._cards = [Card(rank) for rank in ranks]

    def draw(self) -> Card:
        return self._cards.pop(0)

    @property
    def needs_shuffle(self) -> bool:
        return False

    @property
    def remaining_cards(self) -> int:
        return len(self._cards)

    def reset(self) -> None:
        raise AssertionError("scripted shoe should not reset")


def test_trace_event_serializes_decimal_details() -> None:
    event = TraceEvent(
        event_type=TraceEventType.INITIAL_BET_PLACED,
        sequence=1,
        round_number=3,
        hand_id="player_0",
        details={"amount": Decimal("10")},
    )

    assert event.to_dict() == {
        "type": "initial_bet_placed",
        "sequence": 1,
        "round_number": 3,
        "hand_id": "player_0",
        "details": {"amount": "10"},
    }


def test_trace_collector_preserves_event_order() -> None:
    collector = TraceCollector()

    first = collector.record(TraceEventType.ROUND_STARTED, round_number=1)
    second = collector.record(TraceEventType.ROUND_SETTLED, round_number=1)

    assert [event.sequence for event in collector.events] == [1, 2]
    assert first.sequence < second.sequence


def test_simulation_trace_captures_deal_actions_and_settlement() -> None:
    collector = TraceCollector()
    shoe = ScriptedShoe(
        Rank.TEN,
        Rank.SIX,
        Rank.FIVE,
        Rank.NINE,
        Rank.SIX,
        Rank.KING,
    )

    result = run_simulation(
        shoe=shoe,
        config=SimulationConfig(
            rounds=1,
            initial_bankroll=Decimal("100"),
            betting_amount=Decimal("10"),
            dealer_rules=DealerRules(),
        ),
        player_strategy=FixedActionStrategy(Action.HIT, Action.STAND),
        trace_collector=collector,
    )

    event_types = [event.event_type for event in collector.events]
    assert result.final_bankroll == Decimal("110")
    assert TraceEventType.ROUND_STARTED in event_types
    assert TraceEventType.INITIAL_BET_PLACED in event_types
    assert TraceEventType.CARD_DEALT in event_types
    assert TraceEventType.PLAYER_HIT in event_types
    assert TraceEventType.PLAYER_STOOD in event_types
    assert TraceEventType.HAND_SETTLED in event_types
    assert TraceEventType.ROUND_SETTLED in event_types


def test_trace_does_not_change_simulation_result() -> None:
    config = SimulationConfig(
        rounds=1,
        initial_bankroll=Decimal("100"),
        betting_amount=Decimal("10"),
        dealer_rules=DealerRules(),
    )
    ranks = (
        Rank.TEN,
        Rank.SIX,
        Rank.FIVE,
        Rank.NINE,
        Rank.SIX,
        Rank.KING,
    )

    untraced = run_simulation(
        shoe=ScriptedShoe(*ranks),
        config=config,
        player_strategy=FixedActionStrategy(Action.HIT, Action.STAND),
    )
    traced = run_simulation(
        shoe=ScriptedShoe(*ranks),
        config=config,
        player_strategy=FixedActionStrategy(Action.HIT, Action.STAND),
        trace_collector=TraceCollector(),
    )

    assert traced.final_bankroll == untraced.final_bankroll
    assert [round_result.net_result for round_result in traced.rounds] == [
        round_result.net_result for round_result in untraced.rounds
    ]

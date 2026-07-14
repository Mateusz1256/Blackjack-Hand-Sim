from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.engine import SimulationConfig, run_simulation
from blackjack_simulator.round import FixedActionStrategy
from blackjack_simulator.rules import DealerRules, SplitRules


class ScriptedShoe:
    def __init__(self, *ranks: Rank) -> None:
        self._cards = [Card(rank) for rank in ranks]

    def draw(self) -> Card:
        return self._cards.pop(0)

    @property
    def needs_shuffle(self) -> bool:
        return False

    def reset(self) -> None:
        raise AssertionError("scripted shoe should not reset")


def test_simulation_bankroll_includes_all_split_hand_net_results() -> None:
    shoe = ScriptedShoe(
        Rank.EIGHT,
        Rank.TEN,
        Rank.EIGHT,
        Rank.SIX,
        Rank.THREE,
        Rank.TWO,
        Rank.KING,
    )
    config = SimulationConfig(
        rounds=1,
        initial_bankroll=Decimal("100"),
        betting_amount=Decimal("10"),
        dealer_rules=DealerRules(),
        split_rules=SplitRules(allowed=True),
    )

    result = run_simulation(
        shoe=shoe,
        config=config,
        player_strategy=FixedActionStrategy(Action.SPLIT, Action.STAND, Action.STAND),
    )

    assert result.rounds[0].net_result == Decimal("20")
    assert result.final_bankroll == Decimal("120")

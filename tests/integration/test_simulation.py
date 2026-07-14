from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.engine import SimulationConfig, run_simulation
from blackjack_simulator.round import FixedActionStrategy
from blackjack_simulator.rules import DealerRules


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


def test_multi_round_simulation_updates_bankroll_from_net_results() -> None:
    shoe = ScriptedShoe(
        Rank.TEN,
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
        Rank.KING,
        Rank.TEN,
        Rank.TEN,
        Rank.SEVEN,
        Rank.NINE,
    )
    config = SimulationConfig(
        rounds=2,
        initial_bankroll=Decimal("100"),
        betting_amount=Decimal("10"),
        blackjack_payout=Decimal("1.5"),
        dealer_rules=DealerRules(),
    )

    result = run_simulation(
        shoe=shoe,
        config=config,
        player_strategy=FixedActionStrategy(Action.STAND),
    )

    round_nets = [round_result.settlement.net_result for round_result in result.rounds]
    assert round_nets == [Decimal("10"), Decimal("-10")]
    assert result.final_bankroll == Decimal("100")
    assert result.final_bankroll == result.initial_bankroll + sum(round_nets)

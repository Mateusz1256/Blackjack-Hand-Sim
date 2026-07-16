from decimal import Decimal

import pytest

from blackjack_simulator.actions import Action
from blackjack_simulator.betting import (
    BankrollPercentageBettingStrategy,
    BetRoundingMode,
    BetRoundingPolicy,
    DAlembertBettingStrategy,
    FibonacciBettingStrategy,
    FlatBettingStrategy,
    KellyStyleBettingStrategy,
    MartingaleBettingStrategy,
    ParoliBettingStrategy,
    TableLimits,
)
from blackjack_simulator.betting.base import BettingOutcome
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.engine import SimulationConfig, run_simulation
from blackjack_simulator.exceptions import InsufficientBankrollError
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


def test_flat_betting_clamps_to_table_minimum() -> None:
    strategy = FlatBettingStrategy(
        amount=Decimal("5"),
        table_limits=TableLimits(minimum=Decimal("10"), maximum=Decimal("100")),
    )

    assert strategy.next_bet(Decimal("100")) == Decimal("10")


def test_table_maximum_caps_progressive_bet() -> None:
    strategy = MartingaleBettingStrategy(
        base_amount=Decimal("10"),
        table_limits=TableLimits(minimum=Decimal("10"), maximum=Decimal("25")),
    )

    strategy.update_after_round(BettingOutcome.LOSS)
    strategy.update_after_round(BettingOutcome.LOSS)

    assert strategy.next_bet(Decimal("100")) == Decimal("25")


def test_insufficient_bankroll_raises_when_below_table_minimum() -> None:
    strategy = FlatBettingStrategy(
        amount=Decimal("10"),
        table_limits=TableLimits(minimum=Decimal("10"), maximum=Decimal("100")),
    )

    with pytest.raises(InsufficientBankrollError):
        strategy.next_bet(Decimal("9"))


def test_bankroll_percentage_bet_sizing_with_rounding() -> None:
    strategy = BankrollPercentageBettingStrategy(
        percentage=Decimal("0.025"),
        rounding=BetRoundingPolicy(
            mode=BetRoundingMode.NEAREST,
            increment=Decimal("5"),
        ),
    )

    assert strategy.next_bet(Decimal("1000")) == Decimal("25")
    assert strategy.next_bet(Decimal("880")) == Decimal("20")


def test_kelly_style_bet_uses_documented_assumptions() -> None:
    strategy = KellyStyleBettingStrategy(
        edge=Decimal("0.02"),
        variance=Decimal("1"),
        fraction=Decimal("0.5"),
        rounding=BetRoundingPolicy(
            mode=BetRoundingMode.FLOOR,
            increment=Decimal("1"),
        ),
    )

    assert strategy.next_bet(Decimal("1000")) == Decimal("10")


def test_martingale_doubles_after_loss_resets_after_win_and_ignores_push() -> None:
    strategy = MartingaleBettingStrategy(base_amount=Decimal("10"))

    strategy.update_after_round(BettingOutcome.LOSS)
    assert strategy.next_bet(Decimal("100")) == Decimal("20")

    strategy.update_after_round(BettingOutcome.PUSH)
    assert strategy.next_bet(Decimal("100")) == Decimal("20")

    strategy.update_after_round(BettingOutcome.WIN)
    assert strategy.next_bet(Decimal("100")) == Decimal("10")


def test_paroli_doubles_after_win_resets_after_loss_and_ignores_push() -> None:
    strategy = ParoliBettingStrategy(base_amount=Decimal("10"), max_wins=2)

    strategy.update_after_round(BettingOutcome.WIN)
    assert strategy.next_bet(Decimal("100")) == Decimal("20")

    strategy.update_after_round(BettingOutcome.PUSH)
    assert strategy.next_bet(Decimal("100")) == Decimal("20")

    strategy.update_after_round(BettingOutcome.WIN)
    assert strategy.next_bet(Decimal("100")) == Decimal("40")

    strategy.update_after_round(BettingOutcome.LOSS)
    assert strategy.next_bet(Decimal("100")) == Decimal("10")


def test_fibonacci_advances_on_loss_steps_back_two_on_win_and_ignores_push() -> None:
    strategy = FibonacciBettingStrategy(base_amount=Decimal("10"))

    strategy.update_after_round(BettingOutcome.LOSS)
    strategy.update_after_round(BettingOutcome.LOSS)
    strategy.update_after_round(BettingOutcome.LOSS)
    assert strategy.next_bet(Decimal("100")) == Decimal("30")

    strategy.update_after_round(BettingOutcome.PUSH)
    assert strategy.next_bet(Decimal("100")) == Decimal("30")

    strategy.update_after_round(BettingOutcome.WIN)
    assert strategy.next_bet(Decimal("100")) == Decimal("10")


def test_dalembert_moves_one_unit_after_loss_or_win_and_ignores_push() -> None:
    strategy = DAlembertBettingStrategy(base_amount=Decimal("10"))

    strategy.update_after_round(BettingOutcome.LOSS)
    strategy.update_after_round(BettingOutcome.LOSS)
    assert strategy.next_bet(Decimal("100")) == Decimal("30")

    strategy.update_after_round(BettingOutcome.PUSH)
    assert strategy.next_bet(Decimal("100")) == Decimal("30")

    strategy.update_after_round(BettingOutcome.WIN)
    assert strategy.next_bet(Decimal("100")) == Decimal("20")


def test_engine_updates_betting_strategy_once_for_split_round() -> None:
    class CountingBettingStrategy(FlatBettingStrategy):
        updates: int

        def __init__(self) -> None:
            super().__init__(amount=Decimal("10"))
            self.updates = 0

        def update_after_round(self, outcome: BettingOutcome) -> None:
            self.updates += 1
            self.last_outcome = outcome

    betting_strategy = CountingBettingStrategy()
    shoe = ScriptedShoe(
        Rank.EIGHT,
        Rank.TEN,
        Rank.EIGHT,
        Rank.SIX,
        Rank.THREE,
        Rank.TWO,
        Rank.KING,
    )

    run_simulation(
        shoe=shoe,
        config=SimulationConfig(
            rounds=1,
            initial_bankroll=Decimal("100"),
            betting_amount=Decimal("10"),
            dealer_rules=DealerRules(),
            split_rules=SplitRules(allowed=True),
        ),
        player_strategy=FixedActionStrategy(Action.SPLIT, Action.STAND, Action.STAND),
        betting_strategy=betting_strategy,
    )

    assert betting_strategy.updates == 1
    assert betting_strategy.last_outcome is BettingOutcome.WIN


def test_simulation_stops_on_stop_loss() -> None:
    shoe = ScriptedShoe(Rank.TEN, Rank.TEN, Rank.SEVEN, Rank.KING)

    result = run_simulation(
        shoe=shoe,
        config=SimulationConfig(
            rounds=3,
            initial_bankroll=Decimal("100"),
            betting_amount=Decimal("10"),
            dealer_rules=DealerRules(peeks_for_blackjack=False),
            stop_loss=Decimal("10"),
        ),
        player_strategy=FixedActionStrategy(Action.STAND),
    )

    assert result.statistics is None
    assert result.stop_reason is not None
    assert result.stop_reason.value == "stop_loss"
    assert len(result.rounds) == 1


def test_simulation_stops_on_stop_win() -> None:
    shoe = ScriptedShoe(Rank.TEN, Rank.TEN, Rank.KING, Rank.SEVEN)

    result = run_simulation(
        shoe=shoe,
        config=SimulationConfig(
            rounds=3,
            initial_bankroll=Decimal("100"),
            betting_amount=Decimal("10"),
            dealer_rules=DealerRules(peeks_for_blackjack=False),
            stop_win=Decimal("10"),
        ),
        player_strategy=FixedActionStrategy(Action.STAND),
    )

    assert result.stop_reason is not None
    assert result.stop_reason.value == "stop_win"
    assert len(result.rounds) == 1

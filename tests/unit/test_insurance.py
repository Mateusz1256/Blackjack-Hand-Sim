from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.round import FixedActionStrategy, play_round
from blackjack_simulator.rules import DealerRules, InsuranceRules
from blackjack_simulator.settlement import InsuranceOutcome, Outcome
from blackjack_simulator.strategies.insurance import (
    AlwaysInsuranceStrategy,
    EvenMoneyInsuranceStrategy,
    NeverInsuranceStrategy,
)


class StubShoe:
    def __init__(self, *ranks: Rank) -> None:
        self._cards = [Card(rank) for rank in ranks]

    def draw(self) -> Card:
        return self._cards.pop(0)

    @property
    def needs_shuffle(self) -> bool:
        return False

    def reset(self) -> None:
        raise AssertionError("stub shoe should not reset")


def test_insurance_wins_when_dealer_has_blackjack() -> None:
    shoe = StubShoe(Rank.TEN, Rank.ACE, Rank.SIX, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=True),
        insurance_rules=InsuranceRules(offered=True),
        insurance_strategy=AlwaysInsuranceStrategy(),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
    )

    assert result.insurance_settlement is not None
    assert result.insurance_settlement.outcome is InsuranceOutcome.WIN
    assert result.insurance_settlement.bet == Decimal("5.0")
    assert result.insurance_settlement.net_result == Decimal("10.0")
    assert result.settlement.outcome is Outcome.DEALER_BLACKJACK
    assert result.net_result == Decimal("0.0")


def test_insurance_loses_when_dealer_does_not_have_blackjack() -> None:
    shoe = StubShoe(Rank.TEN, Rank.ACE, Rank.SIX, Rank.NINE, Rank.TWO)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=True),
        insurance_rules=InsuranceRules(offered=True),
        insurance_strategy=AlwaysInsuranceStrategy(),
        player_strategy=FixedActionStrategy(Action.STAND),
        bet=Decimal("10"),
    )

    assert result.insurance_settlement is not None
    assert result.insurance_settlement.outcome is InsuranceOutcome.LOSS
    assert result.insurance_settlement.net_result == Decimal("-5.0")
    assert result.net_result == Decimal("-15.0")


def test_never_insurance_strategy_declines_side_bet() -> None:
    shoe = StubShoe(Rank.TEN, Rank.ACE, Rank.SIX, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=True),
        insurance_rules=InsuranceRules(offered=True),
        insurance_strategy=NeverInsuranceStrategy(),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
    )

    assert result.insurance_settlement is None
    assert result.net_result == Decimal("-10")


def test_even_money_on_player_blackjack_against_dealer_ace() -> None:
    shoe = StubShoe(Rank.ACE, Rank.ACE, Rank.KING, Rank.NINE)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=True),
        insurance_rules=InsuranceRules(offered=True),
        insurance_strategy=EvenMoneyInsuranceStrategy(),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
    )

    assert result.player_hand.is_blackjack()
    assert result.insurance_settlement is not None
    assert result.insurance_settlement.outcome is InsuranceOutcome.LOSS
    assert result.settlement.outcome is Outcome.PLAYER_BLACKJACK
    assert result.net_result == Decimal("10.0")


def test_peek_with_ten_upcard_ends_round_before_player_actions() -> None:
    shoe = StubShoe(Rank.NINE, Rank.TEN, Rank.SEVEN, Rank.ACE)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=True),
        insurance_rules=InsuranceRules(offered=True),
        insurance_strategy=AlwaysInsuranceStrategy(),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
    )

    assert result.player_hand.cards == [Card(Rank.NINE), Card(Rank.SEVEN)]
    assert result.settlement.outcome is Outcome.DEALER_BLACKJACK
    assert result.insurance_settlement is None


def test_insurance_not_offered_without_dealer_ace() -> None:
    shoe = StubShoe(Rank.TEN, Rank.TEN, Rank.SIX, Rank.NINE)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=True),
        insurance_rules=InsuranceRules(offered=True),
        insurance_strategy=AlwaysInsuranceStrategy(),
        player_strategy=FixedActionStrategy(Action.STAND),
        bet=Decimal("10"),
    )

    assert result.insurance_settlement is None

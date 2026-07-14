from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.round import FixedActionStrategy, play_round
from blackjack_simulator.rules import (
    DealerRules,
    DoubleRules,
    EnhcLossRule,
    HoleCardMode,
    HoleCardRules,
    SplitRules,
)
from blackjack_simulator.settlement import Outcome


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


def test_enhc_dealer_gets_second_card_after_player_actions() -> None:
    shoe = StubShoe(Rank.TEN, Rank.ACE, Rank.SEVEN, Rank.NINE)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        hole_card_rules=HoleCardRules(mode=HoleCardMode.EUROPEAN_NO_HOLE_CARD),
        player_strategy=FixedActionStrategy(Action.STAND),
        bet=Decimal("10"),
    )

    assert [card.rank for card in result.dealer_hand.cards] == [Rank.ACE, Rank.NINE]
    assert result.settlement.outcome is Outcome.DEALER_WIN


def test_enhc_all_bets_lost_after_double_against_dealer_blackjack() -> None:
    shoe = StubShoe(Rank.FIVE, Rank.ACE, Rank.SIX, Rank.FIVE, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        hole_card_rules=HoleCardRules(
            mode=HoleCardMode.EUROPEAN_NO_HOLE_CARD,
            enhc_loss_rule=EnhcLossRule.ALL_BETS,
        ),
        double_rules=DoubleRules(allowed=True),
        player_strategy=FixedActionStrategy(Action.DOUBLE),
        bet=Decimal("10"),
    )

    assert result.player_hand.doubled
    assert result.player_hand.current_bet == Decimal("20")
    assert result.settlement.outcome is Outcome.DEALER_BLACKJACK
    assert result.settlement.net_result == Decimal("-20")


def test_enhc_original_bet_only_after_double_against_dealer_blackjack() -> None:
    shoe = StubShoe(Rank.FIVE, Rank.ACE, Rank.SIX, Rank.FIVE, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        hole_card_rules=HoleCardRules(
            mode=HoleCardMode.EUROPEAN_NO_HOLE_CARD,
            enhc_loss_rule=EnhcLossRule.ORIGINAL_BET_ONLY,
        ),
        double_rules=DoubleRules(allowed=True),
        player_strategy=FixedActionStrategy(Action.DOUBLE),
        bet=Decimal("10"),
    )

    assert result.player_hand.current_bet == Decimal("20")
    assert result.settlement.outcome is Outcome.DEALER_BLACKJACK
    assert result.settlement.net_result == Decimal("-10")


def test_enhc_split_loses_all_bets_against_dealer_blackjack() -> None:
    shoe = StubShoe(
        Rank.EIGHT,
        Rank.ACE,
        Rank.EIGHT,
        Rank.THREE,
        Rank.TWO,
        Rank.KING,
    )

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        hole_card_rules=HoleCardRules(
            mode=HoleCardMode.EUROPEAN_NO_HOLE_CARD,
            enhc_loss_rule=EnhcLossRule.ALL_BETS,
        ),
        split_rules=SplitRules(allowed=True),
        player_strategy=FixedActionStrategy(Action.SPLIT, Action.STAND, Action.STAND),
        bet=Decimal("10"),
    )

    assert [settlement.net_result for settlement in result.settlements] == [
        Decimal("-10"),
        Decimal("-10"),
    ]
    assert result.net_result == Decimal("-20")


def test_enhc_split_original_bet_only_loses_once_against_dealer_blackjack() -> None:
    shoe = StubShoe(
        Rank.EIGHT,
        Rank.ACE,
        Rank.EIGHT,
        Rank.THREE,
        Rank.TWO,
        Rank.KING,
    )

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        hole_card_rules=HoleCardRules(
            mode=HoleCardMode.EUROPEAN_NO_HOLE_CARD,
            enhc_loss_rule=EnhcLossRule.ORIGINAL_BET_ONLY,
        ),
        split_rules=SplitRules(allowed=True),
        player_strategy=FixedActionStrategy(Action.SPLIT, Action.STAND, Action.STAND),
        bet=Decimal("10"),
    )

    assert [settlement.net_result for settlement in result.settlements] == [
        Decimal("-10"),
        Decimal("0"),
    ]
    assert result.net_result == Decimal("-10")

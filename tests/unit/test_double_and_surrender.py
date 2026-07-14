from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.hand import Hand
from blackjack_simulator.round import FixedActionStrategy, play_round
from blackjack_simulator.rules import (
    DealerRules,
    DoubleRules,
    SurrenderRules,
    SurrenderType,
    can_double,
    can_surrender,
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


def test_double_adds_one_base_bet_draws_one_card_and_settles() -> None:
    shoe = StubShoe(Rank.FIVE, Rank.TEN, Rank.SIX, Rank.SEVEN, Rank.SEVEN)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        double_rules=DoubleRules(allowed=True),
        player_strategy=FixedActionStrategy(Action.DOUBLE),
        bet=Decimal("10"),
    )

    assert result.player_hand.doubled
    assert result.player_hand.current_bet == Decimal("20")
    assert [card.rank for card in result.player_hand.cards] == [
        Rank.FIVE,
        Rank.SIX,
        Rank.SEVEN,
    ]
    assert result.settlement.outcome is Outcome.PLAYER_WIN
    assert result.settlement.net_result == Decimal("20")


def test_double_restriction_falls_back_to_hit_for_strategy() -> None:
    shoe = StubShoe(Rank.FIVE, Rank.TEN, Rank.FIVE, Rank.SEVEN, Rank.NINE, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        double_rules=DoubleRules(allowed=True, allowed_totals=frozenset({11})),
        player_strategy=FixedActionStrategy(Action.DOUBLE, Action.STAND),
        bet=Decimal("10"),
    )

    assert not result.player_hand.doubled
    assert result.player_hand.current_bet == Decimal("10")
    assert [card.rank for card in result.player_hand.cards] == [
        Rank.FIVE,
        Rank.FIVE,
        Rank.NINE,
    ]


def test_can_double_rejects_non_two_card_hand() -> None:
    shoe = StubShoe(Rank.FIVE, Rank.TEN, Rank.FIVE, Rank.SEVEN, Rank.NINE, Rank.KING)
    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        double_rules=DoubleRules(allowed=True),
        player_strategy=FixedActionStrategy(Action.HIT, Action.DOUBLE, Action.STAND),
        bet=Decimal("10"),
    )

    assert not can_double(result.player_hand, DoubleRules(allowed=True))
    assert not result.player_hand.doubled


def test_late_surrender_loses_half_bet_after_no_dealer_blackjack() -> None:
    shoe = StubShoe(Rank.TEN, Rank.ACE, Rank.SIX, Rank.SEVEN)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        surrender_rules=SurrenderRules(SurrenderType.LATE),
        player_strategy=FixedActionStrategy(Action.SURRENDER),
        bet=Decimal("10"),
    )

    assert result.player_hand.surrendered
    assert result.settlement.outcome is Outcome.PLAYER_SURRENDER
    assert result.settlement.net_result == Decimal("-5")


def test_late_surrender_is_not_allowed_when_dealer_has_blackjack() -> None:
    shoe = StubShoe(Rank.TEN, Rank.ACE, Rank.SIX, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        surrender_rules=SurrenderRules(SurrenderType.LATE),
        player_strategy=FixedActionStrategy(Action.SURRENDER),
        bet=Decimal("10"),
    )

    assert not result.player_hand.surrendered
    assert result.settlement.outcome is Outcome.DEALER_BLACKJACK
    assert result.settlement.net_result == Decimal("-10")


def test_early_surrender_is_allowed_before_dealer_blackjack_resolution() -> None:
    shoe = StubShoe(Rank.TEN, Rank.ACE, Rank.SIX, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        surrender_rules=SurrenderRules(SurrenderType.EARLY),
        player_strategy=FixedActionStrategy(Action.SURRENDER),
        bet=Decimal("10"),
    )

    assert result.player_hand.surrendered
    assert result.settlement.outcome is Outcome.PLAYER_SURRENDER
    assert result.settlement.net_result == Decimal("-5")


def test_can_surrender_requires_two_cards_and_configured_rule() -> None:
    hand = Hand(
        cards=[
            Card(Rank.TEN),
            Card(Rank.TWO),
            Card(Rank.THREE),
        ],
    )

    assert not can_surrender(
        hand,
        SurrenderRules(SurrenderType.LATE),
        dealer_blackjack_checked=True,
    )

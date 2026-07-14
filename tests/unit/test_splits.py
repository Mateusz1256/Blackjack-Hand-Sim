from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.hand import Hand
from blackjack_simulator.round import FixedActionStrategy, play_round
from blackjack_simulator.rules import (
    DealerRules,
    DoubleRules,
    SplitRules,
    can_split,
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


def hand_with(*ranks: Rank, is_split_hand: bool = False) -> Hand:
    return Hand(cards=[Card(rank) for rank in ranks], is_split_hand=is_split_hand)


def test_split_creates_two_hands_and_settles_both_bets() -> None:
    shoe = StubShoe(
        Rank.EIGHT,
        Rank.TEN,
        Rank.EIGHT,
        Rank.SIX,
        Rank.THREE,
        Rank.TWO,
        Rank.KING,
        Rank.KING,
    )

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        split_rules=SplitRules(allowed=True, max_hands=4),
        player_strategy=FixedActionStrategy(Action.SPLIT, Action.STAND, Action.STAND),
        bet=Decimal("10"),
    )

    assert len(result.player_hands) == 2
    assert [hand.current_bet for hand in result.player_hands] == [
        Decimal("10"),
        Decimal("10"),
    ]
    assert result.net_result == Decimal("20")
    assert [settlement.outcome for settlement in result.settlements] == [
        Outcome.DEALER_BUST,
        Outcome.DEALER_BUST,
    ]


def test_split_hands_are_played_in_order() -> None:
    shoe = StubShoe(
        Rank.SIX,
        Rank.TEN,
        Rank.SIX,
        Rank.SEVEN,
        Rank.FIVE,
        Rank.FOUR,
        Rank.KING,
        Rank.KING,
    )

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        split_rules=SplitRules(allowed=True, max_hands=4),
        player_strategy=FixedActionStrategy(
            Action.SPLIT,
            Action.HIT,
            Action.STAND,
            Action.STAND,
        ),
        bet=Decimal("10"),
    )

    assert [[card.rank for card in hand.cards] for hand in result.player_hands] == [
        [Rank.SIX, Rank.FIVE, Rank.KING],
        [Rank.SIX, Rank.FOUR],
    ]


def test_split_limit_prevents_resplit_after_max_hands() -> None:
    first = hand_with(Rank.EIGHT, Rank.EIGHT)
    second = hand_with(Rank.EIGHT, Rank.EIGHT, is_split_hand=True)

    rules = SplitRules(allowed=True, max_hands=2)

    assert can_split(first, rules, current_hand_count=1)
    assert not can_split(second, rules, current_hand_count=2)


def test_split_aces_receive_one_card_and_do_not_hit_by_default() -> None:
    shoe = StubShoe(
        Rank.ACE,
        Rank.TEN,
        Rank.ACE,
        Rank.SEVEN,
        Rank.KING,
        Rank.QUEEN,
    )

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        split_rules=SplitRules(allowed=True, hit_split_aces=False),
        player_strategy=FixedActionStrategy(Action.SPLIT, Action.HIT, Action.HIT),
        bet=Decimal("10"),
    )

    assert [[card.rank for card in hand.cards] for hand in result.player_hands] == [
        [Rank.ACE, Rank.KING],
        [Rank.ACE, Rank.QUEEN],
    ]
    assert all(hand.originated_from_split_aces for hand in result.player_hands)


def test_resplit_aces_requires_explicit_rule() -> None:
    hand = Hand(
        cards=[Card(Rank.ACE), Card(Rank.ACE)],
        is_split_hand=True,
        originated_from_split_aces=True,
    )

    assert not can_split(
        hand,
        SplitRules(allowed=True, resplit_aces=False),
        current_hand_count=2,
    )
    assert can_split(
        hand,
        SplitRules(allowed=True, resplit_aces=True, max_hands=4),
        current_hand_count=2,
    )


def test_twenty_one_after_split_is_not_blackjack_by_default() -> None:
    shoe = StubShoe(
        Rank.ACE,
        Rank.TEN,
        Rank.ACE,
        Rank.SEVEN,
        Rank.KING,
        Rank.QUEEN,
    )

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        split_rules=SplitRules(allowed=True),
        player_strategy=FixedActionStrategy(Action.SPLIT),
        bet=Decimal("10"),
    )

    assert not result.player_hands[0].is_blackjack()
    assert result.player_hands[0].value == 21
    assert result.settlements[0].outcome is Outcome.PLAYER_WIN


def test_double_after_split_requires_rule() -> None:
    split_hand = Hand(
        cards=[Card(Rank.FIVE), Card(Rank.SIX)],
        original_bet=Decimal("10"),
        current_bet=Decimal("10"),
        is_split_hand=True,
    )

    assert Action.DOUBLE not in SplitRules(allowed=True).legal_actions_for(
        split_hand,
        DoubleRules(allowed=True, after_split=False),
        current_hand_count=2,
    )
    assert Action.DOUBLE in SplitRules(allowed=True).legal_actions_for(
        split_hand,
        DoubleRules(allowed=True, after_split=True),
        current_hand_count=2,
    )

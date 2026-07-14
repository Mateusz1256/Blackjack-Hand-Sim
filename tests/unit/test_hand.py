from decimal import Decimal

from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.hand import Hand


def hand_with(*ranks: Rank, is_split_hand: bool = False) -> Hand:
    return Hand(
        cards=[Card(rank) for rank in ranks],
        original_bet=Decimal("10"),
        current_bet=Decimal("10"),
        is_split_hand=is_split_hand,
    )


def test_hard_hand_value() -> None:
    hand = hand_with(Rank.TEN, Rank.SEVEN)

    assert hand.value == 17
    assert not hand.is_soft


def test_soft_seventeen_with_single_ace() -> None:
    hand = hand_with(Rank.ACE, Rank.SIX)

    assert hand.value == 17
    assert hand.is_soft


def test_ace_converts_from_eleven_to_one_to_avoid_bust() -> None:
    hand = hand_with(Rank.ACE, Rank.SIX, Rank.TEN)

    assert hand.value == 17
    assert not hand.is_soft


def test_multiple_aces_keep_one_soft_when_possible() -> None:
    hand = hand_with(Rank.ACE, Rank.ACE, Rank.FIVE)

    assert hand.value == 17
    assert hand.is_soft


def test_multiple_aces_can_make_twenty_one() -> None:
    hand = hand_with(Rank.ACE, Rank.ACE, Rank.NINE)

    assert hand.value == 21
    assert hand.is_soft


def test_bust_detection() -> None:
    hand = hand_with(Rank.KING, Rank.QUEEN, Rank.TWO)

    assert hand.value == 22
    assert hand.is_bust


def test_natural_blackjack() -> None:
    hand = hand_with(Rank.ACE, Rank.KING)

    assert hand.is_blackjack()
    assert hand.value == 21


def test_twenty_one_with_more_than_two_cards_is_not_blackjack() -> None:
    hand = hand_with(Rank.ACE, Rank.FIVE, Rank.FIVE)

    assert hand.value == 21
    assert not hand.is_blackjack()


def test_twenty_one_after_split_is_not_blackjack_by_default() -> None:
    hand = hand_with(Rank.ACE, Rank.TEN, is_split_hand=True)

    assert hand.value == 21
    assert not hand.is_blackjack()


def test_twenty_one_after_split_can_count_as_blackjack_when_rule_allows_it() -> None:
    hand = hand_with(Rank.ACE, Rank.TEN, is_split_hand=True)

    assert hand.is_blackjack(blackjack_after_split_counts_as_blackjack=True)


def test_same_rank_pair_detection() -> None:
    hand = hand_with(Rank.TEN, Rank.TEN)

    assert hand.is_pair()


def test_ten_value_cards_are_not_pair_when_same_rank_is_required() -> None:
    hand = hand_with(Rank.KING, Rank.QUEEN)

    assert not hand.is_pair(require_same_rank=True)


def test_ten_value_cards_can_pair_when_same_rank_is_not_required() -> None:
    hand = hand_with(Rank.KING, Rank.QUEEN)

    assert hand.is_pair(require_same_rank=False)


def test_hand_with_more_than_two_cards_is_not_pair() -> None:
    hand = hand_with(Rank.EIGHT, Rank.EIGHT, Rank.TWO)

    assert not hand.is_pair()

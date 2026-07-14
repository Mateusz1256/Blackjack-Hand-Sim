from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import DealerRules, dealer_should_hit, play_dealer_hand


def hand_with(*ranks: Rank) -> Hand:
    return Hand(cards=[Card(rank) for rank in ranks])


class StubShoe:
    def __init__(self, *ranks: Rank) -> None:
        self._cards = [Card(rank) for rank in ranks]

    def draw(self) -> Card:
        return self._cards.pop(0)


def test_dealer_hits_below_seventeen() -> None:
    assert dealer_should_hit(hand_with(Rank.TEN, Rank.SIX), DealerRules())


def test_dealer_stands_on_hard_seventeen() -> None:
    assert not dealer_should_hit(hand_with(Rank.TEN, Rank.SEVEN), DealerRules())


def test_s17_dealer_stands_on_soft_seventeen() -> None:
    rules = DealerRules(hits_soft_17=False)

    assert not dealer_should_hit(hand_with(Rank.ACE, Rank.SIX), rules)


def test_h17_dealer_hits_soft_seventeen() -> None:
    rules = DealerRules(hits_soft_17=True)

    assert dealer_should_hit(hand_with(Rank.ACE, Rank.SIX), rules)


def test_dealer_stands_above_seventeen() -> None:
    assert not dealer_should_hit(hand_with(Rank.TEN, Rank.EIGHT), DealerRules())


def test_play_dealer_hand_draws_until_s17_stand() -> None:
    hand = hand_with(Rank.ACE, Rank.FIVE)
    shoe = StubShoe(Rank.ACE)

    completed = play_dealer_hand(hand, shoe, DealerRules(hits_soft_17=False))

    assert completed is hand
    assert [card.rank for card in hand.cards] == [Rank.ACE, Rank.FIVE, Rank.ACE]
    assert hand.value == 17
    assert hand.is_soft


def test_play_dealer_hand_draws_on_h17_soft_seventeen() -> None:
    hand = hand_with(Rank.ACE, Rank.SIX)
    shoe = StubShoe(Rank.TWO)

    play_dealer_hand(hand, shoe, DealerRules(hits_soft_17=True))

    assert [card.rank for card in hand.cards] == [Rank.ACE, Rank.SIX, Rank.TWO]
    assert hand.value == 19

from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.round import FixedActionStrategy, play_round
from blackjack_simulator.rules import DealerRules
from blackjack_simulator.settlement import Outcome


class StubShoe:
    def __init__(self, *ranks: Rank) -> None:
        self._cards = [Card(rank) for rank in ranks]
        self.reset_count = 0

    def draw(self) -> Card:
        return self._cards.pop(0)

    @property
    def needs_shuffle(self) -> bool:
        return False

    def reset(self) -> None:
        self.reset_count += 1


def test_round_deals_initial_cards_and_player_can_stand() -> None:
    shoe = StubShoe(Rank.TEN, Rank.NINE, Rank.EIGHT, Rank.SEVEN, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        player_strategy=FixedActionStrategy(Action.STAND),
        bet=Decimal("10"),
    )

    assert [card.rank for card in result.player_hand.cards] == [Rank.TEN, Rank.EIGHT]
    assert [card.rank for card in result.dealer_hand.cards] == [
        Rank.NINE,
        Rank.SEVEN,
        Rank.KING,
    ]
    assert result.settlement.outcome is Outcome.DEALER_BUST
    assert result.settlement.net_result == Decimal("10")


def test_round_player_hits_until_strategy_stands() -> None:
    shoe = StubShoe(Rank.FIVE, Rank.TEN, Rank.FIVE, Rank.SIX, Rank.NINE, Rank.KING)
    strategy = FixedActionStrategy(Action.HIT, Action.STAND)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        player_strategy=strategy,
        bet=Decimal("10"),
    )

    assert [card.rank for card in result.player_hand.cards] == [
        Rank.FIVE,
        Rank.FIVE,
        Rank.NINE,
    ]
    assert result.player_hand.value == 19
    assert result.settlement.outcome is Outcome.DEALER_BUST


def test_round_stops_immediately_when_player_busts() -> None:
    shoe = StubShoe(Rank.TEN, Rank.SIX, Rank.NINE, Rank.FIVE, Rank.KING)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
    )

    assert result.player_hand.is_bust
    assert [card.rank for card in result.dealer_hand.cards] == [Rank.SIX, Rank.FIVE]
    assert result.settlement.outcome is Outcome.PLAYER_BUST


def test_round_settles_initial_blackjack_before_player_actions() -> None:
    shoe = StubShoe(Rank.ACE, Rank.TEN, Rank.KING, Rank.SEVEN)

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
    )

    assert result.settlement.outcome is Outcome.PLAYER_BLACKJACK
    assert result.settlement.net_result == Decimal("15.0")


def test_round_resets_shoe_after_round_when_cut_card_was_reached() -> None:
    class ResettingShoe(StubShoe):
        @property
        def needs_shuffle(self) -> bool:
            return True

    shoe = ResettingShoe(Rank.TEN, Rank.NINE, Rank.EIGHT, Rank.SEVEN, Rank.KING)

    play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        player_strategy=FixedActionStrategy(Action.STAND),
        bet=Decimal("10"),
    )

    assert shoe.reset_count == 1

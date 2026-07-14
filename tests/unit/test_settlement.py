from decimal import Decimal

from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.hand import Hand
from blackjack_simulator.settlement import Outcome, settle_hand


def hand_with(*ranks: Rank, bet: Decimal = Decimal("10")) -> Hand:
    return Hand(
        cards=[Card(rank) for rank in ranks],
        original_bet=bet,
        current_bet=bet,
    )


def test_player_blackjack_pays_configured_net_profit() -> None:
    result = settle_hand(
        player=hand_with(Rank.ACE, Rank.KING),
        dealer=hand_with(Rank.TEN, Rank.SEVEN),
        blackjack_payout=Decimal("1.5"),
    )

    assert result.outcome is Outcome.PLAYER_BLACKJACK
    assert result.net_result == Decimal("15.0")


def test_blackjack_push_returns_zero_net_result() -> None:
    result = settle_hand(
        player=hand_with(Rank.ACE, Rank.KING),
        dealer=hand_with(Rank.ACE, Rank.QUEEN),
        blackjack_payout=Decimal("1.5"),
    )

    assert result.outcome is Outcome.PUSH
    assert result.net_result == Decimal("0")


def test_player_bust_loses_current_bet() -> None:
    result = settle_hand(
        player=hand_with(Rank.TEN, Rank.NINE, Rank.FIVE),
        dealer=hand_with(Rank.TEN, Rank.SIX),
        blackjack_payout=Decimal("1.5"),
    )

    assert result.outcome is Outcome.PLAYER_BUST
    assert result.net_result == Decimal("-10")


def test_dealer_bust_pays_even_money() -> None:
    result = settle_hand(
        player=hand_with(Rank.TEN, Rank.EIGHT),
        dealer=hand_with(Rank.TEN, Rank.NINE, Rank.FIVE),
        blackjack_payout=Decimal("1.5"),
    )

    assert result.outcome is Outcome.DEALER_BUST
    assert result.net_result == Decimal("10")


def test_higher_player_total_wins_even_money() -> None:
    result = settle_hand(
        player=hand_with(Rank.TEN, Rank.NINE),
        dealer=hand_with(Rank.TEN, Rank.EIGHT),
        blackjack_payout=Decimal("1.5"),
    )

    assert result.outcome is Outcome.PLAYER_WIN
    assert result.net_result == Decimal("10")


def test_higher_dealer_total_loses_current_bet() -> None:
    result = settle_hand(
        player=hand_with(Rank.TEN, Rank.SEVEN),
        dealer=hand_with(Rank.TEN, Rank.EIGHT),
        blackjack_payout=Decimal("1.5"),
    )

    assert result.outcome is Outcome.DEALER_WIN
    assert result.net_result == Decimal("-10")


def test_equal_totals_push() -> None:
    result = settle_hand(
        player=hand_with(Rank.TEN, Rank.EIGHT),
        dealer=hand_with(Rank.QUEEN, Rank.EIGHT),
        blackjack_payout=Decimal("1.5"),
    )

    assert result.outcome is Outcome.PUSH
    assert result.net_result == Decimal("0")

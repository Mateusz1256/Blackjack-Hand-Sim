from blackjack_simulator.cards import Card, Rank, card_value


def test_numeric_card_values_match_rank() -> None:
    assert card_value(Card(Rank.TWO)) == 2
    assert card_value(Card(Rank.NINE)) == 9


def test_face_cards_have_value_ten() -> None:
    assert card_value(Card(Rank.TEN)) == 10
    assert card_value(Card(Rank.JACK)) == 10
    assert card_value(Card(Rank.QUEEN)) == 10
    assert card_value(Card(Rank.KING)) == 10


def test_ace_base_value_is_eleven() -> None:
    assert card_value(Card(Rank.ACE)) == 11

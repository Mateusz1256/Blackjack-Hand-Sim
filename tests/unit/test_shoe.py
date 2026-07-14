import random
from collections import Counter

import pytest

from blackjack_simulator.cards import Rank
from blackjack_simulator.shoe import Shoe


def test_shoe_contains_expected_cards_for_multiple_decks() -> None:
    shoe = Shoe(decks=2, penetration=0.75, rng=random.Random(1))

    counts = Counter(card.rank for card in shoe.cards)

    assert len(shoe.cards) == 104
    assert counts[Rank.ACE] == 8
    assert counts[Rank.TEN] == 8
    assert counts[Rank.JACK] == 8
    assert counts[Rank.QUEEN] == 8
    assert counts[Rank.KING] == 8
    assert all(count == 8 for rank, count in counts.items() if rank is not Rank.TEN)


def test_shoe_order_is_deterministic_for_same_seed() -> None:
    first = Shoe(decks=6, penetration=0.75, rng=random.Random(123))
    second = Shoe(decks=6, penetration=0.75, rng=random.Random(123))

    assert [card.rank for card in first.cards] == [card.rank for card in second.cards]


def test_drawing_cards_advances_remaining_count() -> None:
    shoe = Shoe(decks=1, penetration=0.75, rng=random.Random(1))

    first_card = shoe.draw()
    second_card = shoe.draw()

    assert first_card != second_card or len(shoe.cards) == 50
    assert shoe.cards_dealt == 2
    assert shoe.remaining_cards == 50


def test_penetration_threshold_is_not_reached_before_cut_card() -> None:
    shoe = Shoe(decks=1, penetration=0.75, rng=random.Random(1))

    for _ in range(38):
        shoe.draw()

    assert not shoe.needs_shuffle


def test_penetration_threshold_is_reached_at_cut_card() -> None:
    shoe = Shoe(decks=1, penetration=0.75, rng=random.Random(1))

    for _ in range(39):
        shoe.draw()

    assert shoe.needs_shuffle


def test_shuffle_after_each_round_always_requests_shuffle_after_round() -> None:
    shoe = Shoe(
        decks=1,
        penetration=0.75,
        rng=random.Random(1),
        shuffle_after_each_round=True,
    )

    assert shoe.needs_shuffle


def test_reset_shuffles_new_shoe_and_clears_dealt_count() -> None:
    rng = random.Random(1)
    shoe = Shoe(decks=1, penetration=0.75, rng=rng)
    original_order = [card.rank for card in shoe.cards]
    shoe.draw()

    shoe.reset()

    assert shoe.cards_dealt == 0
    assert shoe.remaining_cards == 52
    assert [card.rank for card in shoe.cards] != original_order


@pytest.mark.parametrize(
    ("decks", "penetration"),
    [
        (0, 0.75),
        (-1, 0.75),
        (1, 0),
        (1, 1.01),
    ],
)
def test_invalid_shoe_configuration_is_rejected(decks: int, penetration: float) -> None:
    with pytest.raises(ValueError, match=r"decks|penetration"):
        Shoe(decks=decks, penetration=penetration, rng=random.Random(1))

"""Card primitives for blackjack."""

from dataclasses import dataclass
from enum import StrEnum


class Rank(StrEnum):
    """Blackjack card ranks.

    Suits are intentionally not modeled because they do not affect blackjack
    hand values in the planned simulator.
    """

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


@dataclass(frozen=True, slots=True)
class Card:
    """A blackjack card represented by rank only."""

    rank: Rank


_CARD_VALUES: dict[Rank, int] = {
    Rank.TWO: 2,
    Rank.THREE: 3,
    Rank.FOUR: 4,
    Rank.FIVE: 5,
    Rank.SIX: 6,
    Rank.SEVEN: 7,
    Rank.EIGHT: 8,
    Rank.NINE: 9,
    Rank.TEN: 10,
    Rank.JACK: 10,
    Rank.QUEEN: 10,
    Rank.KING: 10,
    Rank.ACE: 11,
}


def card_value(card: Card) -> int:
    """Return the blackjack base value for a single card.

    Aces return 11 here. Hand-level ace adjustment lives in `Hand`, where the
    whole card set is available.
    """

    return _CARD_VALUES[card.rank]


def is_ace(card: Card) -> bool:
    return card.rank is Rank.ACE


def is_ten_value(card: Card) -> bool:
    return card_value(card) == 10

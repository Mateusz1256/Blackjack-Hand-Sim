"""Hi-Lo card counting system."""

from dataclasses import dataclass
from decimal import Decimal

from blackjack_simulator.cards import Card, Rank

_HI_LO_VALUES: dict[Rank, int] = {
    Rank.TWO: 1,
    Rank.THREE: 1,
    Rank.FOUR: 1,
    Rank.FIVE: 1,
    Rank.SIX: 1,
    Rank.SEVEN: 0,
    Rank.EIGHT: 0,
    Rank.NINE: 0,
    Rank.TEN: -1,
    Rank.JACK: -1,
    Rank.QUEEN: -1,
    Rank.KING: -1,
    Rank.ACE: -1,
}


@dataclass(slots=True)
class HiLoCounter:
    running_count: int = 0
    cards_seen: int = 0

    def observe(self, card: Card) -> None:
        self.running_count += _HI_LO_VALUES[card.rank]
        self.cards_seen += 1

    def reset(self) -> None:
        self.running_count = 0
        self.cards_seen = 0

    def true_count(self, *, remaining_cards: int) -> Decimal:
        if remaining_cards <= 0:
            return Decimal(self.running_count)

        remaining_decks = Decimal(remaining_cards) / Decimal(52)
        return Decimal(self.running_count) / remaining_decks

"""Deterministic blackjack shoe."""

from dataclasses import dataclass, field
from random import Random

from blackjack_simulator.cards import Card, Rank

_CARDS_PER_DECK = 52


@dataclass(slots=True)
class Shoe:
    """A shuffled blackjack shoe using an injected random generator."""

    decks: int
    penetration: float
    rng: Random
    shuffle_after_each_round: bool = False
    cards: list[Card] = field(init=False)
    cards_dealt: int = field(init=False, default=0)
    cut_card_position: int = field(init=False)

    def __post_init__(self) -> None:
        if self.decks <= 0:
            msg = "decks must be a positive integer"
            raise ValueError(msg)
        if not 0 < self.penetration <= 1:
            msg = "penetration must be greater than 0 and at most 1"
            raise ValueError(msg)

        self.cut_card_position = int(self.total_cards * self.penetration)
        self.reset()

    @property
    def total_cards(self) -> int:
        return self.decks * _CARDS_PER_DECK

    @property
    def remaining_cards(self) -> int:
        return len(self.cards)

    @property
    def needs_shuffle(self) -> bool:
        return (
            self.shuffle_after_each_round or self.cards_dealt >= self.cut_card_position
        )

    def draw(self) -> Card:
        if not self.cards:
            self.reset()

        self.cards_dealt += 1
        return self.cards.pop()

    def reset(self) -> None:
        self.cards = self._build_cards()
        self.rng.shuffle(self.cards)
        self.cards_dealt = 0

    def _build_cards(self) -> list[Card]:
        cards: list[Card] = []
        for _ in range(self.decks):
            for rank in Rank:
                cards.extend(Card(rank) for _ in range(4))

        return cards

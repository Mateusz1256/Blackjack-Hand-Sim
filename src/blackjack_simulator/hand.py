"""Blackjack hand model and value calculation."""

from dataclasses import dataclass, field
from decimal import Decimal

from blackjack_simulator.cards import Card, card_value, is_ace, is_ten_value


@dataclass(slots=True)
class Hand:
    """A player hand with enough state for future round flow and settlement."""

    cards: list[Card] = field(default_factory=list)
    original_bet: Decimal = Decimal("0")
    current_bet: Decimal = Decimal("0")
    is_split_hand: bool = False
    split_depth: int = 0
    originated_from_split_aces: bool = False
    doubled: bool = False
    surrendered: bool = False
    stood: bool = False
    completed: bool = False

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    @property
    def value(self) -> int:
        total = sum(card_value(card) for card in self.cards)
        soft_aces = sum(1 for card in self.cards if is_ace(card))

        while total > 21 and soft_aces > 0:
            total -= 10
            soft_aces -= 1

        return total

    @property
    def is_soft(self) -> bool:
        total = sum(card_value(card) for card in self.cards)
        soft_aces = sum(1 for card in self.cards if is_ace(card))

        while total > 21 and soft_aces > 0:
            total -= 10
            soft_aces -= 1

        return soft_aces > 0

    @property
    def is_bust(self) -> bool:
        return self.value > 21

    def is_blackjack(
        self, *, blackjack_after_split_counts_as_blackjack: bool = False
    ) -> bool:
        if len(self.cards) != 2:
            return False
        if self.is_split_hand and not blackjack_after_split_counts_as_blackjack:
            return False

        first, second = self.cards
        return (is_ace(first) and is_ten_value(second)) or (
            is_ace(second) and is_ten_value(first)
        )

    def is_pair(self, *, require_same_rank: bool = True) -> bool:
        if len(self.cards) != 2:
            return False

        first, second = self.cards
        if require_same_rank:
            return first.rank is second.rank

        return card_value(first) == card_value(second)

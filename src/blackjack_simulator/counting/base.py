"""Card counting protocols."""

from decimal import Decimal
from typing import Protocol

from blackjack_simulator.cards import Card


class CardCounter(Protocol):
    running_count: int
    cards_seen: int

    def observe(self, card: Card) -> None:
        """Observe a revealed card."""

    def reset(self) -> None:
        """Reset count state after shuffle."""

    def true_count(self, *, remaining_cards: int) -> Decimal:
        """Return true count from remaining shoe cards."""

"""Strategy protocols."""

from typing import Protocol

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card
from blackjack_simulator.hand import Hand


class PlayingStrategy(Protocol):
    def choose_action(self, hand: Hand, dealer_upcard: Card) -> Action:
        """Choose the next action for a player hand."""

"""Table rule primitives used by domain components."""

from dataclasses import dataclass
from typing import Protocol

from blackjack_simulator.cards import Card
from blackjack_simulator.hand import Hand


class CardSource(Protocol):
    def draw(self) -> Card:
        """Draw and return the next card."""


@dataclass(frozen=True, slots=True)
class DealerRules:
    """Dealer drawing rules.

    `hits_soft_17=False` represents S17. `hits_soft_17=True` represents H17.
    """

    hits_soft_17: bool = False


def dealer_should_hit(hand: Hand, rules: DealerRules) -> bool:
    if hand.value < 17:
        return True
    if hand.value > 17:
        return False

    return hand.is_soft and rules.hits_soft_17


def play_dealer_hand(hand: Hand, shoe: CardSource, rules: DealerRules) -> Hand:
    while dealer_should_hit(hand, rules):
        hand.add_card(shoe.draw())

    return hand

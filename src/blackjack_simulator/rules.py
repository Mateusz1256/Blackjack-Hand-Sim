"""Table rule primitives used by domain components."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from blackjack_simulator.actions import Action
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


@dataclass(frozen=True, slots=True)
class DoubleRules:
    allowed: bool = False
    after_split: bool = False
    allowed_totals: frozenset[int] | None = None


class SurrenderType(StrEnum):
    NONE = "none"
    LATE = "late"
    EARLY = "early"


@dataclass(frozen=True, slots=True)
class SurrenderRules:
    surrender_type: SurrenderType = SurrenderType.NONE


def can_double(hand: Hand, rules: DoubleRules) -> bool:
    if not rules.allowed:
        return False
    if len(hand.cards) != 2:
        return False
    if hand.is_split_hand and not rules.after_split:
        return False
    return rules.allowed_totals is None or hand.value in rules.allowed_totals


def can_surrender(
    hand: Hand,
    rules: SurrenderRules,
    *,
    dealer_blackjack_checked: bool,
) -> bool:
    if rules.surrender_type is SurrenderType.NONE:
        return False
    if len(hand.cards) != 2:
        return False
    if hand.is_split_hand:
        return False
    if rules.surrender_type is SurrenderType.EARLY:
        return not dealer_blackjack_checked
    if rules.surrender_type is SurrenderType.LATE:
        return dealer_blackjack_checked

    return False


def legal_player_actions(
    hand: Hand,
    *,
    double_rules: DoubleRules,
    surrender_rules: SurrenderRules,
    dealer_blackjack_checked: bool,
) -> frozenset[Action]:
    actions = {Action.HIT, Action.STAND}
    if can_double(hand, double_rules):
        actions.add(Action.DOUBLE)
    if can_surrender(
        hand,
        surrender_rules,
        dealer_blackjack_checked=dealer_blackjack_checked,
    ):
        actions.add(Action.SURRENDER)

    return frozenset(actions)


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

"""Table rule primitives used by domain components."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
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


@dataclass(frozen=True, slots=True)
class SplitRules:
    allowed: bool = False
    max_hands: int = 4
    require_same_rank: bool = True
    resplit_aces: bool = False
    hit_split_aces: bool = False
    double_after_split_aces: bool = False
    blackjack_after_split_counts_as_blackjack: bool = False

    def legal_actions_for(
        self,
        hand: Hand,
        double_rules: DoubleRules,
        *,
        current_hand_count: int,
    ) -> frozenset[Action]:
        return legal_player_actions(
            hand,
            double_rules=double_rules,
            surrender_rules=SurrenderRules(),
            split_rules=self,
            dealer_blackjack_checked=True,
            current_hand_count=current_hand_count,
        )


def can_double(hand: Hand, rules: DoubleRules) -> bool:
    if not rules.allowed:
        return False
    if len(hand.cards) != 2:
        return False
    if hand.is_split_hand and not rules.after_split:
        return False
    return rules.allowed_totals is None or hand.value in rules.allowed_totals


def can_double_with_split_rules(
    hand: Hand,
    double_rules: DoubleRules,
    split_rules: SplitRules,
) -> bool:
    if not can_double(hand, double_rules):
        return False
    return not hand.originated_from_split_aces or split_rules.double_after_split_aces


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
    split_rules: SplitRules | None = None,
    dealer_blackjack_checked: bool,
    current_hand_count: int = 1,
) -> frozenset[Action]:
    actions = {Action.HIT, Action.STAND}
    split_rules = split_rules or SplitRules()
    if can_double_with_split_rules(hand, double_rules, split_rules):
        actions.add(Action.DOUBLE)
    if can_split(hand, split_rules, current_hand_count=current_hand_count):
        actions.add(Action.SPLIT)
    if can_surrender(
        hand,
        surrender_rules,
        dealer_blackjack_checked=dealer_blackjack_checked,
    ):
        actions.add(Action.SURRENDER)

    return frozenset(actions)


def can_split(
    hand: Hand,
    rules: SplitRules,
    *,
    current_hand_count: int,
) -> bool:
    if not rules.allowed:
        return False
    if current_hand_count >= rules.max_hands:
        return False
    if len(hand.cards) != 2:
        return False
    if not hand.is_pair(require_same_rank=rules.require_same_rank):
        return False
    return not (_is_aces_pair(hand) and hand.is_split_hand and not rules.resplit_aces)


def _is_aces_pair(hand: Hand) -> bool:
    return len(hand.cards) == 2 and all(card.rank is Rank.ACE for card in hand.cards)


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

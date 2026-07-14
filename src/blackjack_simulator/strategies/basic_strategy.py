"""Table-driven basic strategy with legal-action fallback."""

from collections.abc import Set
from dataclasses import dataclass, field
from enum import StrEnum

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank, card_value
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import DealerRules
from blackjack_simulator.strategies.basic_strategy_tables import (
    BasicStrategyTables,
    StrategyDecision,
    get_tables,
)


class BasicStrategyProfile(StrEnum):
    S17 = "s17"
    H17 = "h17"


@dataclass(frozen=True, slots=True)
class BasicStrategy:
    profile: BasicStrategyProfile
    legal_actions: Set[Action] = field(
        default_factory=lambda: frozenset({Action.HIT, Action.STAND})
    )
    tables: BasicStrategyTables = field(init=False)

    def __post_init__(self) -> None:
        if (
            Action.HIT not in self.legal_actions
            or Action.STAND not in self.legal_actions
        ):
            msg = "basic strategy requires hit and stand fallback actions"
            raise ValueError(msg)

        object.__setattr__(self, "tables", get_tables(self.profile))

    def choose_action(
        self,
        hand: Hand,
        dealer_upcard: Card,
        legal_actions: frozenset[Action] | None = None,
    ) -> Action:
        decision = self.preferred_decision(hand, dealer_upcard)
        return self._to_legal_action(
            decision,
            hand,
            dealer_upcard,
            legal_actions or self.legal_actions,
        )

    def preferred_decision(self, hand: Hand, dealer_upcard: Card) -> StrategyDecision:
        dealer_value = _dealer_upcard_value(dealer_upcard)

        if hand.is_pair() and len(hand.cards) == 2:
            return self.tables.pairs[hand.cards[0].rank][dealer_value]
        if hand.is_soft and hand.value in self.tables.soft:
            return self.tables.soft[hand.value][dealer_value]

        return self.tables.hard[_hard_total_key(hand.value)][dealer_value]

    def _to_legal_action(
        self,
        decision: StrategyDecision,
        hand: Hand,
        dealer_upcard: Card,
        legal_actions: Set[Action],
    ) -> Action:
        if decision is StrategyDecision.HIT:
            return Action.HIT
        if decision is StrategyDecision.STAND:
            return Action.STAND
        if decision in {StrategyDecision.DOUBLE_HIT, StrategyDecision.DOUBLE_STAND}:
            if Action.DOUBLE in legal_actions:
                return Action.DOUBLE
            if decision is StrategyDecision.DOUBLE_HIT:
                return Action.HIT
            return Action.STAND
        if decision is StrategyDecision.SURRENDER_HIT:
            if Action.SURRENDER in legal_actions:
                return Action.SURRENDER
            return Action.HIT
        if decision is StrategyDecision.SURRENDER_STAND:
            if Action.SURRENDER in legal_actions:
                return Action.SURRENDER
            return Action.STAND
        if decision is StrategyDecision.SPLIT:
            if Action.SPLIT in legal_actions:
                return Action.SPLIT
            return self._pair_fallback(hand, dealer_upcard, legal_actions)

        msg = f"unsupported basic strategy decision: {decision}"
        raise ValueError(msg)

    def _pair_fallback(
        self,
        hand: Hand,
        dealer_upcard: Card,
        legal_actions: Set[Action],
    ) -> Action:
        if len(hand.cards) != 2:
            return Action.HIT
        if hand.cards[0].rank is Rank.ACE:
            return Action.HIT

        dealer_value = _dealer_upcard_value(dealer_upcard)
        if hand.is_soft and hand.value in self.tables.soft:
            fallback = self.tables.soft[hand.value][dealer_value]
        else:
            fallback = self.tables.hard[_hard_total_key(hand.value)][dealer_value]

        return self._to_legal_action(fallback, hand, dealer_upcard, legal_actions)


def basic_strategy_for_rules(
    dealer_rules: DealerRules,
    *,
    legal_actions: Set[Action] | None = None,
) -> BasicStrategy:
    profile = (
        BasicStrategyProfile.H17
        if dealer_rules.hits_soft_17
        else BasicStrategyProfile.S17
    )
    if legal_actions is None:
        return BasicStrategy(profile)

    return BasicStrategy(profile, legal_actions=legal_actions)


def _dealer_upcard_value(card: Card) -> int:
    if card.rank is Rank.ACE:
        return 11

    return min(card_value(card), 10)


def _hard_total_key(total: int) -> int:
    if total < 4:
        return 4
    if total > 21:
        return 21

    return total

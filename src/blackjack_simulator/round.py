"""Basic single-round blackjack flow."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import (
    CardSource,
    DealerRules,
    DoubleRules,
    SurrenderRules,
    SurrenderType,
    legal_player_actions,
    play_dealer_hand,
)
from blackjack_simulator.settlement import SettlementResult, settle_hand


class PlayerStrategy(Protocol):
    def choose_action(
        self,
        hand: Hand,
        dealer_upcard: Card,
        legal_actions: frozenset[Action] | None = None,
    ) -> Action:
        """Return hit or stand for the current hand."""


class RoundShoe(CardSource, Protocol):
    @property
    def needs_shuffle(self) -> bool:
        """Whether the shoe should be reset after this round."""

    def reset(self) -> None:
        """Reset the shoe before a future round."""


@dataclass(frozen=True, slots=True)
class FixedActionStrategy:
    """Deterministic hit/stand strategy for tests and early simulations."""

    actions: tuple[Action, ...]
    _calls: int = 0

    def __init__(self, *actions: Action) -> None:
        object.__setattr__(self, "actions", actions or (Action.STAND,))
        object.__setattr__(self, "_calls", 0)

    def choose_action(
        self,
        hand: Hand,
        dealer_upcard: Card,
        legal_actions: frozenset[Action] | None = None,
    ) -> Action:
        del hand, dealer_upcard, legal_actions
        if len(self.actions) == 1:
            return self.actions[0]

        index = min(self._calls, len(self.actions) - 1)
        action = self.actions[index]
        object.__setattr__(self, "_calls", self._calls + 1)
        return action


@dataclass(frozen=True, slots=True)
class ThresholdStrategy:
    """Simple non-basic strategy: hit below a configured total, otherwise stand."""

    stand_on: int = 17

    def choose_action(
        self,
        hand: Hand,
        dealer_upcard: Card,
        legal_actions: frozenset[Action] | None = None,
    ) -> Action:
        del dealer_upcard, legal_actions
        if hand.value < self.stand_on:
            return Action.HIT

        return Action.STAND


@dataclass(frozen=True, slots=True)
class RoundResult:
    player_hand: Hand
    dealer_hand: Hand
    settlement: SettlementResult


def play_round(
    *,
    shoe: RoundShoe,
    dealer_rules: DealerRules,
    player_strategy: PlayerStrategy,
    bet: Decimal,
    blackjack_payout: Decimal = Decimal("1.5"),
    double_rules: DoubleRules | None = None,
    surrender_rules: SurrenderRules | None = None,
) -> RoundResult:
    double_rules = double_rules or DoubleRules()
    surrender_rules = surrender_rules or SurrenderRules()
    player = Hand(original_bet=bet, current_bet=bet)
    dealer = Hand()

    player.add_card(shoe.draw())
    dealer.add_card(shoe.draw())
    player.add_card(shoe.draw())
    dealer.add_card(shoe.draw())

    if player.is_blackjack():
        return _complete_round(player, dealer, shoe, blackjack_payout)

    if surrender_rules.surrender_type is SurrenderType.EARLY:
        early_legal_actions = legal_player_actions(
            player,
            double_rules=DoubleRules(),
            surrender_rules=surrender_rules,
            dealer_blackjack_checked=False,
        )
        action = _choose_action(
            player_strategy,
            player,
            dealer.cards[0],
            early_legal_actions,
        )
        if action is Action.SURRENDER:
            player.surrendered = True
            return _complete_round(player, dealer, shoe, blackjack_payout)

    if dealer.is_blackjack():
        return _complete_round(player, dealer, shoe, blackjack_payout)

    while not player.is_bust and not player.surrendered:
        legal_actions = legal_player_actions(
            player,
            double_rules=double_rules,
            surrender_rules=surrender_rules,
            dealer_blackjack_checked=True,
        )
        action = _choose_action(player_strategy, player, dealer.cards[0], legal_actions)
        if action not in legal_actions:
            action = _fallback_action(action)
        if action is Action.STAND:
            player.stood = True
            break
        if action is Action.HIT:
            player.add_card(shoe.draw())
            continue
        if action is Action.DOUBLE:
            player.current_bet += player.original_bet
            player.doubled = True
            player.add_card(shoe.draw())
            break
        if action is Action.SURRENDER:
            player.surrendered = True
            break
        msg = f"unsupported action for round flow: {action}"
        raise ValueError(msg)

    if not player.is_bust and not player.surrendered:
        play_dealer_hand(dealer, shoe, dealer_rules)

    return _complete_round(player, dealer, shoe, blackjack_payout)


def _choose_action(
    player_strategy: PlayerStrategy,
    player: Hand,
    dealer_upcard: Card,
    legal_actions: frozenset[Action],
) -> Action:
    return player_strategy.choose_action(player, dealer_upcard, legal_actions)


def _fallback_action(action: Action) -> Action:
    if action is Action.DOUBLE:
        return Action.HIT
    if action is Action.SURRENDER:
        return Action.HIT
    if action is Action.SPLIT:
        return Action.HIT

    return action


def _complete_round(
    player: Hand,
    dealer: Hand,
    shoe: RoundShoe,
    blackjack_payout: Decimal,
) -> RoundResult:
    player.completed = True
    dealer.completed = True
    result = RoundResult(
        player_hand=player,
        dealer_hand=dealer,
        settlement=settle_hand(
            player=player,
            dealer=dealer,
            blackjack_payout=blackjack_payout,
        ),
    )

    if shoe.needs_shuffle:
        shoe.reset()

    return result

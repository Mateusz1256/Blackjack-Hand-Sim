"""Basic single-round blackjack flow."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import CardSource, DealerRules, play_dealer_hand
from blackjack_simulator.settlement import SettlementResult, settle_hand


class PlayerStrategy(Protocol):
    def choose_action(self, hand: Hand, dealer_upcard: Card) -> Action:
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

    def choose_action(self, hand: Hand, dealer_upcard: Card) -> Action:
        del hand, dealer_upcard
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

    def choose_action(self, hand: Hand, dealer_upcard: Card) -> Action:
        del dealer_upcard
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
) -> RoundResult:
    player = Hand(original_bet=bet, current_bet=bet)
    dealer = Hand()

    player.add_card(shoe.draw())
    dealer.add_card(shoe.draw())
    player.add_card(shoe.draw())
    dealer.add_card(shoe.draw())

    if player.is_blackjack() or dealer.is_blackjack():
        return _complete_round(player, dealer, shoe, blackjack_payout)

    while not player.is_bust:
        action = player_strategy.choose_action(player, dealer.cards[0])
        if action is Action.STAND:
            player.stood = True
            break
        if action is Action.HIT:
            player.add_card(shoe.draw())
            continue

    if not player.is_bust:
        play_dealer_hand(dealer, shoe, dealer_rules)

    return _complete_round(player, dealer, shoe, blackjack_payout)


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

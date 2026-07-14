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
    SplitRules,
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
    player_hands: list[Hand]
    dealer_hand: Hand
    settlements: list[SettlementResult]

    @property
    def player_hand(self) -> Hand:
        return self.player_hands[0]

    @property
    def settlement(self) -> SettlementResult:
        return self.settlements[0]

    @property
    def net_result(self) -> Decimal:
        return sum(
            (settlement.net_result for settlement in self.settlements),
            start=Decimal("0"),
        )


def play_round(
    *,
    shoe: RoundShoe,
    dealer_rules: DealerRules,
    player_strategy: PlayerStrategy,
    bet: Decimal,
    blackjack_payout: Decimal = Decimal("1.5"),
    double_rules: DoubleRules | None = None,
    surrender_rules: SurrenderRules | None = None,
    split_rules: SplitRules | None = None,
) -> RoundResult:
    double_rules = double_rules or DoubleRules()
    surrender_rules = surrender_rules or SurrenderRules()
    split_rules = split_rules or SplitRules()
    player = Hand(original_bet=bet, current_bet=bet)
    dealer = Hand()

    player.add_card(shoe.draw())
    dealer.add_card(shoe.draw())
    player.add_card(shoe.draw())
    dealer.add_card(shoe.draw())

    if player.is_blackjack():
        return _complete_round([player], dealer, shoe, blackjack_payout, split_rules)

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
            return _complete_round(
                [player],
                dealer,
                shoe,
                blackjack_payout,
                split_rules,
            )

    if dealer.is_blackjack():
        return _complete_round([player], dealer, shoe, blackjack_payout, split_rules)

    player_hands = [player]
    hand_index = 0
    while hand_index < len(player_hands):
        active_hand = player_hands[hand_index]
        if _split_aces_hand_is_complete(active_hand, split_rules):
            active_hand.completed = True
            hand_index += 1
            continue

        hand_was_split = _play_player_hand(
            active_hand,
            hand_index,
            player_hands,
            shoe,
            dealer.cards[0],
            player_strategy,
            double_rules,
            surrender_rules,
            split_rules,
        )
        if hand_was_split:
            continue
        hand_index += 1

    if any(not hand.is_bust and not hand.surrendered for hand in player_hands):
        play_dealer_hand(dealer, shoe, dealer_rules)

    return _complete_round(player_hands, dealer, shoe, blackjack_payout, split_rules)


def _play_player_hand(
    hand: Hand,
    hand_index: int,
    player_hands: list[Hand],
    shoe: RoundShoe,
    dealer_upcard: Card,
    player_strategy: PlayerStrategy,
    double_rules: DoubleRules,
    surrender_rules: SurrenderRules,
    split_rules: SplitRules,
) -> bool:
    while not hand.is_bust and not hand.surrendered:
        legal_actions = legal_player_actions(
            hand,
            double_rules=double_rules,
            surrender_rules=surrender_rules,
            split_rules=split_rules,
            dealer_blackjack_checked=True,
            current_hand_count=len(player_hands),
        )
        action = _choose_action(player_strategy, hand, dealer_upcard, legal_actions)
        if action not in legal_actions:
            action = _fallback_action(action)
        if action is Action.STAND:
            hand.stood = True
            break
        if action is Action.HIT:
            hand.add_card(shoe.draw())
            continue
        if action is Action.DOUBLE:
            hand.current_bet += hand.original_bet
            hand.doubled = True
            hand.add_card(shoe.draw())
            break
        if action is Action.SURRENDER:
            hand.surrendered = True
            break
        if action is Action.SPLIT:
            player_hands[hand_index : hand_index + 1] = _split_hand(
                hand,
                shoe,
                split_rules,
            )
            return True
        msg = f"unsupported action for round flow: {action}"
        raise ValueError(msg)

    hand.completed = True
    return False


def _split_hand(
    hand: Hand,
    shoe: RoundShoe,
    split_rules: SplitRules,
) -> list[Hand]:
    first_card, second_card = hand.cards
    split_aces = first_card.rank is second_card.rank and first_card.rank.value == "A"
    depth = hand.split_depth + 1
    first = Hand(
        cards=[first_card],
        original_bet=hand.original_bet,
        current_bet=hand.original_bet,
        is_split_hand=True,
        split_depth=depth,
        originated_from_split_aces=hand.originated_from_split_aces or split_aces,
    )
    second = Hand(
        cards=[second_card],
        original_bet=hand.original_bet,
        current_bet=hand.original_bet,
        is_split_hand=True,
        split_depth=depth,
        originated_from_split_aces=hand.originated_from_split_aces or split_aces,
    )
    first.add_card(shoe.draw())
    second.add_card(shoe.draw())

    if split_aces and not split_rules.hit_split_aces:
        first.completed = True
        second.completed = True

    return [first, second]


def _split_aces_hand_is_complete(hand: Hand, split_rules: SplitRules) -> bool:
    return (
        hand.originated_from_split_aces
        and not split_rules.hit_split_aces
        and len(hand.cards) >= 2
    )


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
    player_hands: list[Hand],
    dealer: Hand,
    shoe: RoundShoe,
    blackjack_payout: Decimal,
    split_rules: SplitRules,
) -> RoundResult:
    for hand in player_hands:
        hand.completed = True
    dealer.completed = True
    result = RoundResult(
        player_hands=player_hands,
        dealer_hand=dealer,
        settlements=[
            settle_hand(
                player=hand,
                dealer=dealer,
                blackjack_payout=blackjack_payout,
                blackjack_after_split_counts_as_blackjack=(
                    split_rules.blackjack_after_split_counts_as_blackjack
                ),
            )
            for hand in player_hands
        ],
    )

    if shoe.needs_shuffle:
        shoe.reset()

    return result

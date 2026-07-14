"""Basic single-round blackjack flow."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card
from blackjack_simulator.counting.base import CardCounter
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import (
    CardSource,
    DealerRules,
    DoubleRules,
    HoleCardMode,
    HoleCardRules,
    InsuranceRules,
    SplitRules,
    SurrenderRules,
    SurrenderType,
    dealer_should_peek,
    is_insurance_offered,
    legal_player_actions,
)
from blackjack_simulator.settlement import (
    InsuranceSettlement,
    SettlementResult,
    settle_enhc_dealer_blackjack,
    settle_hand,
    settle_insurance,
)
from blackjack_simulator.strategies.insurance import (
    InsuranceStrategy,
    NeverInsuranceStrategy,
)
from blackjack_simulator.trace import TraceCollector, TraceEventType
from blackjack_simulator.trace.events import TraceValue


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
    insurance_settlement: InsuranceSettlement | None = None

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
        ) + (
            self.insurance_settlement.net_result
            if self.insurance_settlement is not None
            else Decimal("0")
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
    insurance_rules: InsuranceRules | None = None,
    insurance_strategy: InsuranceStrategy | None = None,
    hole_card_rules: HoleCardRules | None = None,
    card_counter: CardCounter | None = None,
    trace_collector: TraceCollector | None = None,
    round_number: int = 1,
) -> RoundResult:
    double_rules = double_rules or DoubleRules()
    surrender_rules = surrender_rules or SurrenderRules()
    split_rules = split_rules or SplitRules()
    insurance_rules = insurance_rules or InsuranceRules()
    insurance_strategy = insurance_strategy or NeverInsuranceStrategy()
    hole_card_rules = hole_card_rules or HoleCardRules()
    player = Hand(original_bet=bet, current_bet=bet)
    dealer = Hand()

    _draw_visible_card(
        shoe,
        player,
        card_counter,
        trace_collector,
        round_number,
        hand_id="player_0",
        recipient="player",
        reason="initial_deal",
    )
    _draw_visible_card(
        shoe,
        dealer,
        card_counter,
        trace_collector,
        round_number,
        hand_id="dealer",
        recipient="dealer",
        reason="initial_deal",
    )
    _draw_visible_card(
        shoe,
        player,
        card_counter,
        trace_collector,
        round_number,
        hand_id="player_0",
        recipient="player",
        reason="initial_deal",
    )
    if hole_card_rules.mode is HoleCardMode.AMERICAN:
        card = shoe.draw()
        dealer.add_card(card)
        _trace(
            trace_collector,
            TraceEventType.CARD_DEALT,
            round_number=round_number,
            hand_id="dealer",
            details={
                "recipient": "dealer",
                "card": _card_token(card),
                "visible": False,
                "reason": "hole_card",
            },
        )

    insurance_settlement = _resolve_insurance(
        player=player,
        dealer=dealer,
        rules=insurance_rules,
        strategy=insurance_strategy,
        remaining_cards=_remaining_cards(shoe),
    )

    if player.is_blackjack():
        _reveal_dealer_hole_card(dealer, card_counter)
        _complete_enhc_dealer_initial_hand(dealer, shoe, hole_card_rules, card_counter)
        return _complete_round(
            [player],
            dealer,
            shoe,
            blackjack_payout,
            split_rules,
            insurance_settlement,
            hole_card_rules,
            card_counter,
            trace_collector,
            round_number,
        )

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
            trace_collector,
            round_number,
            "player_0",
        )
        if action is Action.SURRENDER:
            player.surrendered = True
            _trace_player_action(
                trace_collector,
                round_number,
                "player_0",
                TraceEventType.PLAYER_SURRENDERED,
                action,
            )
            return _complete_round(
                [player],
                dealer,
                shoe,
                blackjack_payout,
                split_rules,
                insurance_settlement,
                hole_card_rules,
                card_counter,
                trace_collector,
                round_number,
            )

    if (
        hole_card_rules.mode is HoleCardMode.AMERICAN
        and dealer_should_peek(dealer.cards[0], dealer_rules)
        and dealer.is_blackjack()
    ):
        _reveal_dealer_hole_card(dealer, card_counter)
        return _complete_round(
            [player],
            dealer,
            shoe,
            blackjack_payout,
            split_rules,
            insurance_settlement,
            hole_card_rules,
            card_counter,
            trace_collector,
            round_number,
        )

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
            card_counter,
            trace_collector,
            round_number,
        )
        if hand_was_split:
            continue
        hand_index += 1

    live_hands = [
        hand for hand in player_hands if not hand.is_bust and not hand.surrendered
    ]
    if live_hands:
        _complete_enhc_dealer_initial_hand(dealer, shoe, hole_card_rules, card_counter)
    if (
        hole_card_rules.mode is HoleCardMode.EUROPEAN_NO_HOLE_CARD
        and dealer.is_blackjack()
    ):
        return _complete_round(
            player_hands,
            dealer,
            shoe,
            blackjack_payout,
            split_rules,
            insurance_settlement,
            hole_card_rules,
            card_counter,
            trace_collector,
            round_number,
            enhc_dealer_blackjack=True,
        )
    if live_hands:
        _reveal_dealer_hole_card(dealer, card_counter)
        _play_visible_dealer_hand(
            dealer,
            shoe,
            dealer_rules,
            card_counter,
            trace_collector,
            round_number,
        )

    return _complete_round(
        player_hands,
        dealer,
        shoe,
        blackjack_payout,
        split_rules,
        insurance_settlement,
        hole_card_rules,
        card_counter,
        trace_collector,
        round_number,
    )


def _resolve_insurance(
    *,
    player: Hand,
    dealer: Hand,
    rules: InsuranceRules,
    strategy: InsuranceStrategy,
    remaining_cards: int | None,
) -> InsuranceSettlement | None:
    if len(dealer.cards) < 2:
        return None
    if not is_insurance_offered(dealer.cards[0], rules):
        return None

    insurance_bet = strategy.insurance_bet(
        player=player,
        rules=rules,
        remaining_cards=remaining_cards,
    )
    if insurance_bet <= 0:
        return None

    max_bet = player.current_bet * rules.max_bet_fraction
    if insurance_bet > max_bet:
        insurance_bet = max_bet

    return settle_insurance(
        insurance_bet=insurance_bet,
        dealer_has_blackjack=dealer.is_blackjack(),
        payout=rules.payout,
    )


def _remaining_cards(shoe: RoundShoe) -> int | None:
    return getattr(shoe, "remaining_cards", None)


def _draw_visible_card(
    shoe: RoundShoe,
    hand: Hand,
    card_counter: CardCounter | None,
    trace_collector: TraceCollector | None,
    round_number: int,
    *,
    hand_id: str,
    recipient: str,
    reason: str,
) -> Card:
    card = shoe.draw()
    hand.add_card(card)
    _observe_card(card_counter, card)
    _trace(
        trace_collector,
        TraceEventType.CARD_DEALT,
        round_number=round_number,
        hand_id=hand_id,
        details={
            "recipient": recipient,
            "card": _card_token(card),
            "visible": True,
            "reason": reason,
            "hand_value": hand.value,
        },
    )
    return card


def _observe_card(card_counter: CardCounter | None, card: Card) -> None:
    if card_counter is not None:
        card_counter.observe(card)


def _reveal_dealer_hole_card(
    dealer: Hand,
    card_counter: CardCounter | None,
) -> None:
    if len(dealer.cards) >= 2:
        _observe_card(card_counter, dealer.cards[1])


def _complete_enhc_dealer_initial_hand(
    dealer: Hand,
    shoe: RoundShoe,
    hole_card_rules: HoleCardRules,
    card_counter: CardCounter | None,
    trace_collector: TraceCollector | None = None,
    round_number: int = 1,
) -> None:
    if (
        hole_card_rules.mode is HoleCardMode.EUROPEAN_NO_HOLE_CARD
        and len(dealer.cards) == 1
    ):
        _draw_visible_card(
            shoe,
            dealer,
            card_counter,
            trace_collector,
            round_number,
            hand_id="dealer",
            recipient="dealer",
            reason="enhc_second_card",
        )


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
    card_counter: CardCounter | None,
    trace_collector: TraceCollector | None,
    round_number: int,
) -> bool:
    hand_id = f"player_{hand_index}"
    while not hand.is_bust and not hand.surrendered:
        legal_actions = legal_player_actions(
            hand,
            double_rules=double_rules,
            surrender_rules=surrender_rules,
            split_rules=split_rules,
            dealer_blackjack_checked=True,
            current_hand_count=len(player_hands),
        )
        preferred_action = _choose_action(
            player_strategy,
            hand,
            dealer_upcard,
            legal_actions,
            trace_collector,
            round_number,
            hand_id,
        )
        action = preferred_action
        if action not in legal_actions:
            action = _fallback_action(action)
        _trace(
            trace_collector,
            TraceEventType.STRATEGY_DECISION_RESOLVED,
            round_number=round_number,
            hand_id=hand_id,
            details={
                "preferred_action": preferred_action.value,
                "executed_action": action.value,
                "fallback_applied": action is not preferred_action,
            },
        )
        if action is Action.STAND:
            hand.stood = True
            _trace_player_action(
                trace_collector,
                round_number,
                hand_id,
                TraceEventType.PLAYER_STOOD,
                action,
            )
            break
        if action is Action.HIT:
            _trace_player_action(
                trace_collector,
                round_number,
                hand_id,
                TraceEventType.PLAYER_HIT,
                action,
            )
            _draw_visible_card(
                shoe,
                hand,
                card_counter,
                trace_collector,
                round_number,
                hand_id=hand_id,
                recipient="player",
                reason="hit",
            )
            continue
        if action is Action.DOUBLE:
            hand.current_bet += hand.original_bet
            hand.doubled = True
            _trace_player_action(
                trace_collector,
                round_number,
                hand_id,
                TraceEventType.PLAYER_DOUBLED,
                action,
                {"current_bet": hand.current_bet},
            )
            _draw_visible_card(
                shoe,
                hand,
                card_counter,
                trace_collector,
                round_number,
                hand_id=hand_id,
                recipient="player",
                reason="double",
            )
            break
        if action is Action.SURRENDER:
            hand.surrendered = True
            _trace_player_action(
                trace_collector,
                round_number,
                hand_id,
                TraceEventType.PLAYER_SURRENDERED,
                action,
            )
            break
        if action is Action.SPLIT:
            _trace_player_action(
                trace_collector,
                round_number,
                hand_id,
                TraceEventType.PLAYER_SPLIT,
                action,
            )
            player_hands[hand_index : hand_index + 1] = _split_hand(
                hand,
                shoe,
                split_rules,
                card_counter,
                trace_collector,
                round_number,
                hand_index,
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
    card_counter: CardCounter | None,
    trace_collector: TraceCollector | None,
    round_number: int,
    hand_index: int,
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
    _draw_visible_card(
        shoe,
        first,
        card_counter,
        trace_collector,
        round_number,
        hand_id=f"player_{hand_index}",
        recipient="player",
        reason="split",
    )
    _draw_visible_card(
        shoe,
        second,
        card_counter,
        trace_collector,
        round_number,
        hand_id=f"player_{hand_index + 1}",
        recipient="player",
        reason="split",
    )

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
    trace_collector: TraceCollector | None = None,
    round_number: int = 1,
    hand_id: str | None = None,
) -> Action:
    legal_action_values: list[TraceValue] = [
        action.value for action in sorted(legal_actions, key=lambda item: item.value)
    ]
    _trace(
        trace_collector,
        TraceEventType.STRATEGY_DECISION_REQUESTED,
        round_number=round_number,
        hand_id=hand_id,
        details={
            "hand_value": player.value,
            "dealer_upcard": _card_token(dealer_upcard),
            "legal_actions": legal_action_values,
        },
    )
    return player_strategy.choose_action(player, dealer_upcard, legal_actions)


def _fallback_action(action: Action) -> Action:
    if action is Action.DOUBLE:
        return Action.HIT
    if action is Action.SURRENDER:
        return Action.HIT
    if action is Action.SPLIT:
        return Action.HIT

    return action


def _play_visible_dealer_hand(
    dealer: Hand,
    shoe: RoundShoe,
    dealer_rules: DealerRules,
    card_counter: CardCounter | None,
    trace_collector: TraceCollector | None,
    round_number: int,
) -> Hand:
    while dealer.value < 17 or (
        dealer.value == 17 and dealer.is_soft and dealer_rules.hits_soft_17
    ):
        _draw_visible_card(
            shoe,
            dealer,
            card_counter,
            trace_collector,
            round_number,
            hand_id="dealer",
            recipient="dealer",
            reason="dealer_hit",
        )
        _trace(
            trace_collector,
            TraceEventType.DEALER_HIT,
            round_number=round_number,
            hand_id="dealer",
            details={"hand_value": dealer.value},
        )

    return dealer


def _complete_round(
    player_hands: list[Hand],
    dealer: Hand,
    shoe: RoundShoe,
    blackjack_payout: Decimal,
    split_rules: SplitRules,
    insurance_settlement: InsuranceSettlement | None,
    hole_card_rules: HoleCardRules,
    card_counter: CardCounter | None,
    trace_collector: TraceCollector | None,
    round_number: int,
    *,
    enhc_dealer_blackjack: bool = False,
) -> RoundResult:
    for hand in player_hands:
        hand.completed = True
    dealer.completed = True
    result = RoundResult(
        player_hands=player_hands,
        dealer_hand=dealer,
        settlements=_settle_player_hands(
            player_hands=player_hands,
            dealer=dealer,
            blackjack_payout=blackjack_payout,
            split_rules=split_rules,
            hole_card_rules=hole_card_rules,
            enhc_dealer_blackjack=enhc_dealer_blackjack,
        ),
        insurance_settlement=insurance_settlement,
    )
    for index, settlement in enumerate(result.settlements):
        _trace(
            trace_collector,
            TraceEventType.HAND_SETTLED,
            round_number=round_number,
            hand_id=f"player_{index}",
            details={
                "outcome": settlement.outcome.value,
                "net_result": settlement.net_result,
                "hand_value": result.player_hands[index].value,
                "dealer_value": dealer.value,
            },
        )
    if result.insurance_settlement is not None:
        _trace(
            trace_collector,
            TraceEventType.INSURANCE_SETTLED,
            round_number=round_number,
            hand_id="player_0",
            details={
                "outcome": result.insurance_settlement.outcome.value,
                "bet": result.insurance_settlement.bet,
                "net_result": result.insurance_settlement.net_result,
            },
        )

    if shoe.needs_shuffle:
        shoe.reset()
        if card_counter is not None:
            card_counter.reset()
        _trace(
            trace_collector,
            TraceEventType.SHOE_SHUFFLED,
            round_number=round_number,
        )

    return result


def _settle_player_hands(
    *,
    player_hands: list[Hand],
    dealer: Hand,
    blackjack_payout: Decimal,
    split_rules: SplitRules,
    hole_card_rules: HoleCardRules,
    enhc_dealer_blackjack: bool,
) -> list[SettlementResult]:
    if (
        hole_card_rules.mode is HoleCardMode.EUROPEAN_NO_HOLE_CARD
        and enhc_dealer_blackjack
    ):
        return [
            settle_enhc_dealer_blackjack(
                player=hand,
                loss_rule=hole_card_rules.enhc_loss_rule,
                is_original_hand=index == 0,
            )
            for index, hand in enumerate(player_hands)
        ]

    return [
        settle_hand(
            player=hand,
            dealer=dealer,
            blackjack_payout=blackjack_payout,
            blackjack_after_split_counts_as_blackjack=(
                split_rules.blackjack_after_split_counts_as_blackjack
            ),
        )
        for hand in player_hands
    ]


def _trace_player_action(
    trace_collector: TraceCollector | None,
    round_number: int,
    hand_id: str,
    event_type: TraceEventType,
    action: Action,
    extra_details: dict[str, Decimal] | None = None,
) -> None:
    details: dict[str, TraceValue] = {"action": action.value}
    if extra_details is not None:
        details.update(extra_details)
    _trace(
        trace_collector,
        event_type,
        round_number=round_number,
        hand_id=hand_id,
        details=details,
    )


def _trace(
    trace_collector: TraceCollector | None,
    event_type: TraceEventType,
    *,
    round_number: int,
    hand_id: str | None = None,
    details: dict[str, TraceValue] | None = None,
) -> None:
    if trace_collector is None:
        return
    trace_collector.record(
        event_type,
        round_number=round_number,
        hand_id=hand_id,
        details=details,
    )


def _card_token(card: Card) -> str:
    return card.rank.value

"""Settlement for completed blackjack hands."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import EnhcLossRule


class Outcome(StrEnum):
    PLAYER_BLACKJACK = "player_blackjack"
    PLAYER_BUST = "player_bust"
    PLAYER_SURRENDER = "player_surrender"
    PLAYER_WIN = "player_win"
    DEALER_BLACKJACK = "dealer_blackjack"
    DEALER_BUST = "dealer_bust"
    DEALER_WIN = "dealer_win"
    PUSH = "push"


class InsuranceOutcome(StrEnum):
    WIN = "insurance_win"
    LOSS = "insurance_loss"


@dataclass(frozen=True, slots=True)
class SettlementResult:
    outcome: Outcome
    net_result: Decimal


@dataclass(frozen=True, slots=True)
class InsuranceSettlement:
    outcome: InsuranceOutcome
    bet: Decimal
    net_result: Decimal


def settle_insurance(
    *,
    insurance_bet: Decimal,
    dealer_has_blackjack: bool,
    payout: Decimal,
) -> InsuranceSettlement:
    if dealer_has_blackjack:
        return InsuranceSettlement(
            outcome=InsuranceOutcome.WIN,
            bet=insurance_bet,
            net_result=insurance_bet * payout,
        )

    return InsuranceSettlement(
        outcome=InsuranceOutcome.LOSS,
        bet=insurance_bet,
        net_result=-insurance_bet,
    )


def settle_hand(
    *,
    player: Hand,
    dealer: Hand,
    blackjack_payout: Decimal,
    blackjack_after_split_counts_as_blackjack: bool = False,
) -> SettlementResult:
    bet = player.current_bet
    player_blackjack = player.is_blackjack(
        blackjack_after_split_counts_as_blackjack=(
            blackjack_after_split_counts_as_blackjack
        ),
    )
    dealer_blackjack = dealer.is_blackjack()

    if player.surrendered:
        return SettlementResult(Outcome.PLAYER_SURRENDER, -(bet / Decimal("2")))

    if player_blackjack and dealer_blackjack:
        return SettlementResult(Outcome.PUSH, Decimal("0"))
    if player_blackjack:
        return SettlementResult(Outcome.PLAYER_BLACKJACK, bet * blackjack_payout)
    if dealer_blackjack:
        return SettlementResult(Outcome.DEALER_BLACKJACK, -bet)

    if player.is_bust:
        return SettlementResult(Outcome.PLAYER_BUST, -bet)
    if dealer.is_bust:
        return SettlementResult(Outcome.DEALER_BUST, bet)

    if player.value > dealer.value:
        return SettlementResult(Outcome.PLAYER_WIN, bet)
    if dealer.value > player.value:
        return SettlementResult(Outcome.DEALER_WIN, -bet)

    return SettlementResult(Outcome.PUSH, Decimal("0"))


def settle_enhc_dealer_blackjack(
    *,
    player: Hand,
    loss_rule: EnhcLossRule,
    is_original_hand: bool,
) -> SettlementResult:
    if loss_rule is EnhcLossRule.ALL_BETS:
        return SettlementResult(Outcome.DEALER_BLACKJACK, -player.current_bet)

    if is_original_hand:
        return SettlementResult(Outcome.DEALER_BLACKJACK, -player.original_bet)

    return SettlementResult(Outcome.PUSH, Decimal("0"))

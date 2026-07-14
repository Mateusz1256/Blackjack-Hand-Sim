"""Settlement for completed blackjack hands."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from blackjack_simulator.hand import Hand


class Outcome(StrEnum):
    PLAYER_BLACKJACK = "player_blackjack"
    PLAYER_BUST = "player_bust"
    PLAYER_SURRENDER = "player_surrender"
    PLAYER_WIN = "player_win"
    DEALER_BLACKJACK = "dealer_blackjack"
    DEALER_BUST = "dealer_bust"
    DEALER_WIN = "dealer_win"
    PUSH = "push"


@dataclass(frozen=True, slots=True)
class SettlementResult:
    outcome: Outcome
    net_result: Decimal


def settle_hand(
    *,
    player: Hand,
    dealer: Hand,
    blackjack_payout: Decimal,
) -> SettlementResult:
    bet = player.current_bet
    player_blackjack = player.is_blackjack()
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

"""Martingale betting strategy."""

from dataclasses import dataclass
from decimal import Decimal

from blackjack_simulator.betting.base import (
    BettingOutcome,
    TableLimits,
    apply_limits,
    validate_base_amount,
)


@dataclass(slots=True)
class MartingaleBettingStrategy:
    base_amount: Decimal
    table_limits: TableLimits | None = None
    loss_streak: int = 0

    def __post_init__(self) -> None:
        validate_base_amount(self.base_amount)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        desired = self.base_amount * (Decimal(2) ** self.loss_streak)
        return apply_limits(desired, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        if outcome is BettingOutcome.LOSS:
            self.loss_streak += 1
        elif outcome is BettingOutcome.WIN:
            self.loss_streak = 0

"""Paroli positive progression betting strategy."""

from dataclasses import dataclass
from decimal import Decimal

from blackjack_simulator.betting.base import (
    BettingOutcome,
    TableLimits,
    apply_limits,
    validate_base_amount,
)


@dataclass(slots=True)
class ParoliBettingStrategy:
    base_amount: Decimal
    table_limits: TableLimits | None = None
    max_wins: int = 3
    win_streak: int = 0

    def __post_init__(self) -> None:
        validate_base_amount(self.base_amount)
        if self.max_wins < 1:
            msg = "max_wins must be positive"
            raise ValueError(msg)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        desired = self.base_amount * (Decimal(2) ** min(self.win_streak, self.max_wins))
        return apply_limits(desired, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        if outcome is BettingOutcome.WIN:
            self.win_streak = min(self.win_streak + 1, self.max_wins)
        elif outcome is BettingOutcome.LOSS:
            self.win_streak = 0

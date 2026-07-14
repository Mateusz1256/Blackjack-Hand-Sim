"""Flat betting strategy."""

from dataclasses import dataclass
from decimal import Decimal

from blackjack_simulator.betting.base import (
    BettingOutcome,
    TableLimits,
    apply_limits,
)


@dataclass(slots=True)
class FlatBettingStrategy:
    amount: Decimal
    table_limits: TableLimits | None = None

    def __post_init__(self) -> None:
        if self.amount <= 0:
            msg = "flat betting amount must be positive"
            raise ValueError(msg)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        return apply_limits(self.amount, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        del outcome

"""D'Alembert betting strategy."""

from dataclasses import dataclass
from decimal import Decimal

from blackjack_simulator.betting.base import (
    BettingOutcome,
    TableLimits,
    apply_limits,
    validate_base_amount,
)


@dataclass(slots=True)
class DAlembertBettingStrategy:
    base_amount: Decimal
    table_limits: TableLimits | None = None
    units: int = 1

    def __post_init__(self) -> None:
        validate_base_amount(self.base_amount)
        if self.units < 1:
            msg = "units must be positive"
            raise ValueError(msg)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        desired = self.base_amount * self.units
        return apply_limits(desired, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        if outcome is BettingOutcome.LOSS:
            self.units += 1
        elif outcome is BettingOutcome.WIN:
            self.units = max(1, self.units - 1)

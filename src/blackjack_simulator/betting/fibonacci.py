"""Fibonacci betting strategy."""

from dataclasses import dataclass, field
from decimal import Decimal

from blackjack_simulator.betting.base import (
    BettingOutcome,
    TableLimits,
    apply_limits,
    validate_base_amount,
)


@dataclass(slots=True)
class FibonacciBettingStrategy:
    base_amount: Decimal
    table_limits: TableLimits | None = None
    index: int = 0
    _multipliers: list[int] = field(default_factory=lambda: [1, 1])

    def __post_init__(self) -> None:
        validate_base_amount(self.base_amount)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        self._ensure_index(self.index)
        desired = self.base_amount * self._multipliers[self.index]
        return apply_limits(desired, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        if outcome is BettingOutcome.LOSS:
            self.index += 1
            self._ensure_index(self.index)
        elif outcome is BettingOutcome.WIN:
            self.index = max(0, self.index - 2)

    def _ensure_index(self, index: int) -> None:
        while len(self._multipliers) <= index:
            self._multipliers.append(self._multipliers[-1] + self._multipliers[-2])

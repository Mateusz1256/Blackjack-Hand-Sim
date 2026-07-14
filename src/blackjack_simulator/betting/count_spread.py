"""True-count betting spread."""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal

from blackjack_simulator.betting.base import (
    BettingOutcome,
    TableLimits,
    apply_limits,
    validate_base_amount,
)
from blackjack_simulator.counting.base import CardCounter


@dataclass(slots=True)
class TrueCountSpreadBettingStrategy:
    counter: CardCounter
    base_amount: Decimal
    spread: dict[Decimal, Decimal]
    remaining_cards_provider: Callable[[], int]
    table_limits: TableLimits | None = None

    def __post_init__(self) -> None:
        validate_base_amount(self.base_amount)
        if not self.spread:
            msg = "spread must not be empty"
            raise ValueError(msg)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        true_count = self.counter.true_count(
            remaining_cards=self.remaining_cards_provider(),
        )
        multiplier = Decimal("1")
        for threshold in sorted(self.spread):
            if true_count >= threshold:
                multiplier = self.spread[threshold]

        return apply_limits(self.base_amount * multiplier, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        del outcome

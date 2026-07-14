"""Flat betting strategy."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class FlatBettingStrategy:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount <= 0:
            msg = "flat betting amount must be positive"
            raise ValueError(msg)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        if bankroll < self.amount:
            msg = "bankroll is smaller than the flat betting amount"
            raise ValueError(msg)

        return self.amount

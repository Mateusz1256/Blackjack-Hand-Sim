"""Shared betting strategy primitives."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from blackjack_simulator.exceptions import InsufficientBankrollError


class BettingOutcome(StrEnum):
    WIN = "win"
    LOSS = "loss"
    PUSH = "push"


class BettingStrategy(Protocol):
    def next_bet(self, bankroll: Decimal) -> Decimal:
        """Return the next initial bet for a round."""

    def update_after_round(self, outcome: BettingOutcome) -> None:
        """Update strategy state once after a completed round."""


@dataclass(frozen=True, slots=True)
class TableLimits:
    minimum: Decimal
    maximum: Decimal

    def __post_init__(self) -> None:
        if self.minimum <= 0:
            msg = "table minimum must be positive"
            raise ValueError(msg)
        if self.maximum < self.minimum:
            msg = "table maximum must be greater than or equal to table minimum"
            raise ValueError(msg)

    def clamp(self, desired_bet: Decimal, bankroll: Decimal) -> Decimal:
        if bankroll < self.minimum:
            msg = "bankroll is smaller than the table minimum"
            raise InsufficientBankrollError(msg)

        table_bet = min(max(desired_bet, self.minimum), self.maximum)
        return min(table_bet, bankroll)


def outcome_from_net_result(net_result: Decimal) -> BettingOutcome:
    if net_result > 0:
        return BettingOutcome.WIN
    if net_result < 0:
        return BettingOutcome.LOSS

    return BettingOutcome.PUSH


def validate_base_amount(base_amount: Decimal) -> None:
    if base_amount <= 0:
        msg = "base betting amount must be positive"
        raise ValueError(msg)


def apply_limits(
    desired_bet: Decimal,
    bankroll: Decimal,
    table_limits: TableLimits | None,
) -> Decimal:
    if table_limits is not None:
        return table_limits.clamp(desired_bet, bankroll)
    if bankroll < desired_bet:
        msg = "bankroll is smaller than the requested bet"
        raise InsufficientBankrollError(msg)

    return desired_bet

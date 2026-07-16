"""Advanced bet sizing strategies."""

from dataclasses import dataclass, field
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal
from enum import StrEnum

from blackjack_simulator.betting.base import (
    BettingOutcome,
    TableLimits,
    apply_limits,
)


class BetRoundingMode(StrEnum):
    NONE = "none"
    FLOOR = "floor"
    CEILING = "ceiling"
    NEAREST = "nearest"


@dataclass(frozen=True, slots=True)
class BetRoundingPolicy:
    mode: BetRoundingMode = BetRoundingMode.NONE
    increment: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if self.increment <= 0:
            msg = "bet rounding increment must be positive"
            raise ValueError(msg)

    def round(self, amount: Decimal) -> Decimal:
        if self.mode is BetRoundingMode.NONE:
            return amount

        units = amount / self.increment
        if self.mode is BetRoundingMode.FLOOR:
            rounded_units = units.to_integral_value(rounding=ROUND_FLOOR)
        elif self.mode is BetRoundingMode.CEILING:
            rounded_units = units.to_integral_value(rounding=ROUND_CEILING)
        else:
            rounded_units = units.to_integral_value(rounding=ROUND_HALF_UP)

        return max(self.increment, rounded_units * self.increment)


@dataclass(slots=True)
class BankrollPercentageBettingStrategy:
    percentage: Decimal
    table_limits: TableLimits | None = None
    rounding: BetRoundingPolicy = field(default_factory=BetRoundingPolicy)

    def __post_init__(self) -> None:
        if not 0 < self.percentage <= 1:
            msg = "bankroll percentage must be greater than 0 and at most 1"
            raise ValueError(msg)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        desired = self.rounding.round(bankroll * self.percentage)
        return apply_limits(desired, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        del outcome


@dataclass(slots=True)
class KellyStyleBettingStrategy:
    """Kelly-style sizing with user-supplied edge and variance assumptions."""

    edge: Decimal
    variance: Decimal
    fraction: Decimal = Decimal("1")
    table_limits: TableLimits | None = None
    rounding: BetRoundingPolicy = field(default_factory=BetRoundingPolicy)

    def __post_init__(self) -> None:
        if self.variance <= 0:
            msg = "kelly variance must be positive"
            raise ValueError(msg)
        if self.fraction <= 0:
            msg = "kelly fraction must be positive"
            raise ValueError(msg)

    def next_bet(self, bankroll: Decimal) -> Decimal:
        kelly_fraction = max(Decimal("0"), self.edge / self.variance) * self.fraction
        desired = self.rounding.round(bankroll * kelly_fraction)
        return apply_limits(desired, bankroll, self.table_limits)

    def update_after_round(self, outcome: BettingOutcome) -> None:
        del outcome

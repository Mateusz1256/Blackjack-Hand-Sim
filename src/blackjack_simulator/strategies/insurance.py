"""Insurance strategy implementations."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import InsuranceRules


class InsuranceStrategy(Protocol):
    def insurance_bet(
        self,
        *,
        player: Hand,
        rules: InsuranceRules,
    ) -> Decimal:
        """Return the insurance side bet amount."""


@dataclass(frozen=True, slots=True)
class NeverInsuranceStrategy:
    def insurance_bet(self, *, player: Hand, rules: InsuranceRules) -> Decimal:
        del player, rules
        return Decimal("0")


@dataclass(frozen=True, slots=True)
class AlwaysInsuranceStrategy:
    def insurance_bet(self, *, player: Hand, rules: InsuranceRules) -> Decimal:
        return player.current_bet * rules.max_bet_fraction


@dataclass(frozen=True, slots=True)
class EvenMoneyInsuranceStrategy:
    def insurance_bet(self, *, player: Hand, rules: InsuranceRules) -> Decimal:
        if not player.is_blackjack():
            return Decimal("0")

        return player.current_bet * rules.max_bet_fraction

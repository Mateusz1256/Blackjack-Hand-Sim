"""Insurance strategy implementations."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from blackjack_simulator.counting.base import CardCounter
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import InsuranceRules


class InsuranceStrategy(Protocol):
    def insurance_bet(
        self,
        *,
        player: Hand,
        rules: InsuranceRules,
        remaining_cards: int | None = None,
    ) -> Decimal:
        """Return the insurance side bet amount."""


@dataclass(frozen=True, slots=True)
class NeverInsuranceStrategy:
    def insurance_bet(
        self,
        *,
        player: Hand,
        rules: InsuranceRules,
        remaining_cards: int | None = None,
    ) -> Decimal:
        del player, rules, remaining_cards
        return Decimal("0")


@dataclass(frozen=True, slots=True)
class AlwaysInsuranceStrategy:
    def insurance_bet(
        self,
        *,
        player: Hand,
        rules: InsuranceRules,
        remaining_cards: int | None = None,
    ) -> Decimal:
        del remaining_cards
        return player.current_bet * rules.max_bet_fraction


@dataclass(frozen=True, slots=True)
class EvenMoneyInsuranceStrategy:
    def insurance_bet(
        self,
        *,
        player: Hand,
        rules: InsuranceRules,
        remaining_cards: int | None = None,
    ) -> Decimal:
        del remaining_cards
        if not player.is_blackjack():
            return Decimal("0")

        return player.current_bet * rules.max_bet_fraction


@dataclass(frozen=True, slots=True)
class CountBasedInsuranceStrategy:
    counter: CardCounter
    threshold: Decimal = Decimal("3")

    def insurance_bet(
        self,
        *,
        player: Hand,
        rules: InsuranceRules,
        remaining_cards: int | None = None,
    ) -> Decimal:
        if remaining_cards is None:
            return Decimal("0")
        if self.counter.true_count(remaining_cards=remaining_cards) < self.threshold:
            return Decimal("0")

        return player.current_bet * rules.max_bet_fraction

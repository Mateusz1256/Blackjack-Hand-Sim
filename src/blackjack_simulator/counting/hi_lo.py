"""Hi-Lo card counting system."""

from decimal import Decimal

from blackjack_simulator.cards import Card
from blackjack_simulator.counting.system import (
    ConfigurableCardCounter,
    TrueCountRounding,
    get_counting_system,
)


class HiLoCounter(ConfigurableCardCounter):
    def __init__(
        self,
        *,
        initial_running_count: int | None = None,
        true_count_rounding: TrueCountRounding = TrueCountRounding.NONE,
        min_remaining_decks: Decimal = Decimal("0"),
    ) -> None:
        ConfigurableCardCounter.__init__(
            self,
            system=get_counting_system("hi_lo"),
            initial_running_count=initial_running_count,
            true_count_rounding=true_count_rounding,
            min_remaining_decks=min_remaining_decks,
        )

    def observe(self, card: Card) -> None:
        super().observe(card)

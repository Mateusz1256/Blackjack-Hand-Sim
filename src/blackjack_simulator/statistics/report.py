"""Statistics report data model."""

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class SimulationReport:
    rounds: int
    hands: int
    initial_bankroll: Decimal
    final_bankroll: Decimal
    net_result: Decimal
    total_initial_bet: Decimal
    total_action: Decimal
    average_net_result: Decimal
    sample_variance: Decimal
    population_variance: Decimal
    house_edge_initial_bet: Decimal
    house_edge_total_action: Decimal
    rtp: Decimal
    max_drawdown: Decimal
    longest_win_streak: int
    longest_loss_streak: int
    longest_push_streak: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

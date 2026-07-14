"""Comparison report models."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any

from blackjack_simulator.statistics.report import SimulationReport


class ComparisonMode(StrEnum):
    INDEPENDENT_SEEDS = "independent_seeds"
    COMMON_RANDOM_NUMBERS = "common_random_numbers"


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    name: str
    config_path: Path
    report: SimulationReport
    delta_net_result: Decimal
    delta_house_edge_initial_bet: Decimal
    delta_house_edge_total_action: Decimal
    delta_rtp: Decimal
    delta_average_net_result: Decimal

    def to_dict(self) -> dict[str, Any]:
        payload = self.report.to_dict()
        payload.update(
            {
                "name": self.name,
                "config_path": str(self.config_path),
                "delta_net_result": self.delta_net_result,
                "delta_house_edge_initial_bet": self.delta_house_edge_initial_bet,
                "delta_house_edge_total_action": self.delta_house_edge_total_action,
                "delta_rtp": self.delta_rtp,
                "delta_average_net_result": self.delta_average_net_result,
            },
        )
        return payload


@dataclass(frozen=True, slots=True)
class ComparisonReport:
    mode: ComparisonMode
    baseline: str
    results: tuple[ComparisonResult, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "baseline": self.baseline,
            "notes": list(self.notes),
            "results": [result.to_dict() for result in self.results],
        }

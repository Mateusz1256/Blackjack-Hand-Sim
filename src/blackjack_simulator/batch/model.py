"""Batch simulation report models."""

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class BatchConfig:
    sessions: int
    rounds_per_session: int
    base_seed: int

    def __post_init__(self) -> None:
        if self.sessions <= 0:
            msg = "sessions must be positive"
            raise ValueError(msg)
        if self.rounds_per_session <= 0:
            msg = "rounds per session must be positive"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class BatchSessionResult:
    session_index: int
    seed: int
    rounds_completed: int
    initial_bankroll: Decimal
    final_bankroll: Decimal
    net_result: Decimal
    max_drawdown: Decimal
    ruined: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BatchReport:
    config: BatchConfig
    sessions_completed: int
    ruin_count: int
    risk_of_ruin: Decimal
    profitable_sessions: int
    losing_sessions: int
    breakeven_sessions: int
    profit_rate: Decimal
    loss_rate: Decimal
    breakeven_rate: Decimal
    average_final_bankroll: Decimal
    median_final_bankroll: Decimal
    min_final_bankroll: Decimal
    max_final_bankroll: Decimal
    percentile_final_bankrolls: dict[int, Decimal]
    average_max_drawdown: Decimal
    median_max_drawdown: Decimal
    percentile_max_drawdowns: dict[int, Decimal]
    session_results: tuple[BatchSessionResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

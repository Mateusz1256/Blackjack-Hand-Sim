"""Batch simulation execution and aggregate risk metrics."""

from collections.abc import Sequence
from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
from math import ceil
from random import Random

from blackjack_simulator.batch.model import (
    BatchConfig,
    BatchReport,
    BatchSessionResult,
)
from blackjack_simulator.configuration import AppConfig
from blackjack_simulator.engine import run_simulation
from blackjack_simulator.exceptions import InsufficientBankrollError
from blackjack_simulator.shoe import Shoe
from blackjack_simulator.statistics.collector import StatisticsCollector

_REPORT_PERCENTILES = (5, 25, 50, 75, 95)


def run_batch(app_config: AppConfig, batch_config: BatchConfig) -> BatchReport:
    session_results = tuple(
        _run_session(app_config, batch_config, session_index)
        for session_index in range(batch_config.sessions)
    )
    return build_batch_report(batch_config, session_results)


def build_batch_report(
    config: BatchConfig,
    session_results: Sequence[BatchSessionResult],
) -> BatchReport:
    if not session_results:
        msg = "at least one session result is required"
        raise ValueError(msg)

    completed = len(session_results)
    final_bankrolls = [result.final_bankroll for result in session_results]
    drawdowns = [result.max_drawdown for result in session_results]
    ruin_count = sum(1 for result in session_results if result.ruined)
    profitable = sum(1 for result in session_results if result.net_result > 0)
    losing = sum(1 for result in session_results if result.net_result < 0)
    breakeven = completed - profitable - losing

    return BatchReport(
        config=config,
        sessions_completed=completed,
        ruin_count=ruin_count,
        risk_of_ruin=_rate(ruin_count, completed),
        profitable_sessions=profitable,
        losing_sessions=losing,
        breakeven_sessions=breakeven,
        profit_rate=_rate(profitable, completed),
        loss_rate=_rate(losing, completed),
        breakeven_rate=_rate(breakeven, completed),
        average_final_bankroll=_average(final_bankrolls),
        median_final_bankroll=percentile_nearest_rank(final_bankrolls, 50),
        min_final_bankroll=min(final_bankrolls),
        max_final_bankroll=max(final_bankrolls),
        percentile_final_bankrolls={
            percentile: percentile_nearest_rank(final_bankrolls, percentile)
            for percentile in _REPORT_PERCENTILES
        },
        average_max_drawdown=_average(drawdowns),
        median_max_drawdown=percentile_nearest_rank(drawdowns, 50),
        percentile_max_drawdowns={
            percentile: percentile_nearest_rank(drawdowns, percentile)
            for percentile in _REPORT_PERCENTILES
        },
        session_results=tuple(session_results),
    )


def percentile_nearest_rank(values: Sequence[Decimal], percentile: int) -> Decimal:
    if not values:
        msg = "percentile requires at least one value"
        raise ValueError(msg)
    if not 0 <= percentile <= 100:
        msg = "percentile must be between 0 and 100"
        raise ValueError(msg)

    ordered = sorted(values)
    if percentile == 0:
        return ordered[0]
    index = ceil(percentile / 100 * len(ordered)) - 1
    return ordered[index]


def derive_session_seed(base_seed: int, session_index: int) -> int:
    if session_index < 0:
        msg = "session index must not be negative"
        raise ValueError(msg)

    payload = f"batch:{base_seed}:{session_index}".encode("ascii")
    return int.from_bytes(sha256(payload).digest()[:8], byteorder="big")


def _run_session(
    app_config: AppConfig,
    batch_config: BatchConfig,
    session_index: int,
) -> BatchSessionResult:
    seed = derive_session_seed(batch_config.base_seed, session_index)
    engine_config = replace(
        app_config.engine_config,
        rounds=batch_config.rounds_per_session,
    )
    collector = StatisticsCollector(initial_bankroll=engine_config.initial_bankroll)
    shoe = Shoe(
        decks=app_config.shoe.decks,
        penetration=app_config.shoe.penetration,
        rng=Random(seed),
        shuffle_after_each_round=app_config.shoe.shuffle_after_each_round,
    )
    card_counter = app_config.create_card_counter()
    ruined = False

    try:
        result = run_simulation(
            shoe=shoe,
            config=engine_config,
            player_strategy=app_config.create_playing_strategy(),
            insurance_strategy=app_config.create_insurance_strategy(),
            betting_strategy=app_config.create_betting_strategy(shoe, card_counter),
            card_counter=card_counter,
            statistics_collector=collector,
            store_rounds=False,
        )
        final_bankroll = result.final_bankroll
    except InsufficientBankrollError:
        ruined = True
        final_bankroll = collector.final_bankroll

    ruined = ruined or final_bankroll < engine_config.betting_amount
    return BatchSessionResult(
        session_index=session_index,
        seed=seed,
        rounds_completed=collector.rounds,
        initial_bankroll=engine_config.initial_bankroll,
        final_bankroll=final_bankroll,
        net_result=final_bankroll - engine_config.initial_bankroll,
        max_drawdown=collector.max_drawdown,
        ruined=ruined,
    )


def _average(values: Sequence[Decimal]) -> Decimal:
    return sum(values, Decimal("0")) / Decimal(len(values))


def _rate(count: int, total: int) -> Decimal:
    return Decimal(count) / Decimal(total)

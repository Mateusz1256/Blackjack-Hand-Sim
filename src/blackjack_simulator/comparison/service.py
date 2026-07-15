"""Comparison service using existing simulation interfaces."""

from decimal import Decimal
from pathlib import Path

from blackjack_simulator.comparison.model import (
    ComparisonMode,
    ComparisonReport,
    ComparisonResult,
)
from blackjack_simulator.configuration import load_app_config
from blackjack_simulator.engine import run_simulation, run_worker_simulations
from blackjack_simulator.statistics.collector import StatisticsCollector
from blackjack_simulator.statistics.report import SimulationReport


def compare_configurations(
    config_paths: list[Path],
    *,
    overrides: dict[str, int] | None = None,
    mode: ComparisonMode = ComparisonMode.INDEPENDENT_SEEDS,
) -> ComparisonReport:
    if len(config_paths) < 2:
        msg = "at least two configurations are required for comparison"
        raise ValueError(msg)

    reports: list[tuple[Path, SimulationReport]] = []
    for index, config_path in enumerate(config_paths):
        config_overrides = dict(overrides or {})
        if mode is ComparisonMode.INDEPENDENT_SEEDS and "seed" in config_overrides:
            config_overrides["seed"] += index
        app_config = load_app_config(config_path, overrides=config_overrides)
        reports.append((config_path, _run_report(app_config)))

    baseline_path, baseline_report = reports[0]
    results = tuple(
        _to_result(config_path, report, baseline_report)
        for config_path, report in reports
    )
    notes = _comparison_notes(mode)
    return ComparisonReport(
        mode=mode,
        baseline=baseline_path.name,
        results=results,
        notes=notes,
    )


def _run_report(app_config) -> SimulationReport:  # type: ignore[no-untyped-def]
    if app_config.simulation.workers > 1:
        result = run_worker_simulations(
            config=app_config.engine_config,
            shoe_config=app_config.create_worker_shoe_config(),
            top_level_seed=app_config.simulation.seed,
            worker_count=app_config.simulation.workers,
            player_strategy_factory=app_config.create_playing_strategy_factory(),
            insurance_strategy_factory=app_config.create_insurance_strategy_factory(),
            betting_strategy_factory=app_config.create_betting_strategy_factory(),
            card_counter_factory=app_config.create_card_counter_factory(),
        )
        if result.statistics is None:
            msg = "comparison simulation did not produce statistics"
            raise RuntimeError(msg)
        return result.statistics

    shoe = app_config.create_shoe()
    card_counter = app_config.create_card_counter()
    collector = StatisticsCollector(
        initial_bankroll=app_config.engine_config.initial_bankroll,
    )
    result = run_simulation(
        shoe=shoe,
        config=app_config.engine_config,
        player_strategy=app_config.create_playing_strategy(shoe, card_counter),
        insurance_strategy=app_config.create_insurance_strategy(),
        betting_strategy=app_config.create_betting_strategy(shoe, card_counter),
        card_counter=card_counter,
        statistics_collector=collector,
        store_rounds=False,
    )
    if result.statistics is None:
        msg = "comparison simulation did not produce statistics"
        raise RuntimeError(msg)
    return result.statistics


def _to_result(
    config_path: Path,
    report: SimulationReport,
    baseline: SimulationReport,
) -> ComparisonResult:
    return ComparisonResult(
        name=config_path.stem,
        config_path=config_path,
        report=report,
        delta_net_result=report.net_result - baseline.net_result,
        delta_house_edge_initial_bet=(
            report.house_edge_initial_bet - baseline.house_edge_initial_bet
        ),
        delta_house_edge_total_action=(
            report.house_edge_total_action - baseline.house_edge_total_action
        ),
        delta_rtp=report.rtp - baseline.rtp,
        delta_average_net_result=(
            report.average_net_result - baseline.average_net_result
        ),
    )


def _comparison_notes(mode: ComparisonMode) -> tuple[str, ...]:
    if mode is ComparisonMode.COMMON_RANDOM_NUMBERS:
        return (
            "Common random numbers reuse the same top-level seed, but different "
            "rules can consume different numbers of cards; compare aggregate "
            "metrics rather than assuming hand-by-hand identity.",
        )
    return (
        "Independent seed mode offsets the override seed by configuration index "
        "when a seed override is provided.",
    )


def zero_delta() -> Decimal:
    return Decimal("0")

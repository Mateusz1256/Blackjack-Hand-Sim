"""Simulation worker tasks."""

from collections.abc import Callable
from typing import Any

from blackjack_api.workers.task_queue import CancellationToken, ProgressReporter
from blackjack_simulator.configuration import parse_app_config
from blackjack_simulator.engine import run_simulation, run_worker_simulations
from blackjack_simulator.output.json_output import report_to_json
from blackjack_simulator.statistics.collector import StatisticsCollector
from blackjack_simulator.trace import TraceCollector

CallableSimulationTask = Callable[[ProgressReporter, CancellationToken], dict[str, Any]]


def simulation_task(config_text: str) -> CallableSimulationTask:
    def task(
        report_progress: ProgressReporter,
        cancellation: CancellationToken,
    ) -> dict[str, Any]:
        report_progress(0, 2, "loading_configuration")
        cancellation.raise_if_cancelled()
        app_config = parse_app_config(config_text)
        report_progress(1, 2, "running_simulation")
        cancellation.raise_if_cancelled()

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
        else:
            collector = StatisticsCollector(
                initial_bankroll=app_config.engine_config.initial_bankroll,
            )
            shoe = app_config.create_shoe()
            card_counter = app_config.create_card_counter()
            trace_collector = TraceCollector()
            result = run_simulation(
                shoe=shoe,
                config=app_config.engine_config,
                player_strategy=app_config.create_playing_strategy(shoe, card_counter),
                insurance_strategy=app_config.create_insurance_strategy(),
                betting_strategy=app_config.create_betting_strategy(shoe, card_counter),
                card_counter=card_counter,
                statistics_collector=collector,
                store_rounds=False,
                trace_collector=trace_collector,
            )
            trace_events = trace_collector.to_dicts()
        if app_config.simulation.workers > 1:
            trace_events = []

        if result.statistics is None:
            msg = "simulation did not produce statistics"
            raise RuntimeError(msg)

        report_progress(2, 2, "completed")
        return {
            "report": result.statistics.to_dict(),
            "report_json": report_to_json(result.statistics),
            "stop_reason": (
                result.stop_reason.value if result.stop_reason is not None else None
            ),
            "trace_events": trace_events,
        }

    return task

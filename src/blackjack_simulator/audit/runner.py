"""Audit runner using public configuration, engine, and trace interfaces."""

from dataclasses import dataclass

from blackjack_simulator.audit.checks import AuditInput, build_audit_report
from blackjack_simulator.audit.model import AuditReport
from blackjack_simulator.configuration import AppConfig
from blackjack_simulator.engine import run_simulation
from blackjack_simulator.statistics.collector import StatisticsCollector
from blackjack_simulator.statistics.report import SimulationReport
from blackjack_simulator.trace import TraceCollector, TraceEvent


def run_config_audit(app_config: AppConfig) -> AuditReport:
    first = _run_audited_simulation(app_config)
    second = _run_audited_simulation(app_config)
    deterministic = first.report.to_dict() == second.report.to_dict() and [
        event.to_dict() for event in first.trace_events
    ] == [event.to_dict() for event in second.trace_events]
    return build_audit_report(
        AuditInput(
            report=first.report,
            trace_events=first.trace_events,
            expected_rounds=app_config.engine_config.rounds,
            deterministic=deterministic,
        ),
    )


@dataclass(frozen=True, slots=True)
class _AuditedRun:
    report: SimulationReport
    trace_events: tuple[TraceEvent, ...]


def _run_audited_simulation(app_config: AppConfig) -> _AuditedRun:
    shoe = app_config.create_shoe()
    card_counter = app_config.create_card_counter()
    statistics_collector = StatisticsCollector(
        initial_bankroll=app_config.engine_config.initial_bankroll,
    )
    trace_collector = TraceCollector()
    result = run_simulation(
        shoe=shoe,
        config=app_config.engine_config,
        player_strategy=app_config.create_playing_strategy(),
        insurance_strategy=app_config.create_insurance_strategy(),
        betting_strategy=app_config.create_betting_strategy(shoe, card_counter),
        card_counter=card_counter,
        statistics_collector=statistics_collector,
        store_rounds=False,
        trace_collector=trace_collector,
    )
    if result.statistics is None:
        msg = "audited simulation did not produce statistics"
        raise RuntimeError(msg)
    return _AuditedRun(
        report=result.statistics,
        trace_events=tuple(trace_collector.events),
    )

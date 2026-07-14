"""Audit checks built on simulation reports and trace events."""

from dataclasses import dataclass
from decimal import Decimal

from blackjack_simulator.audit.model import AuditCheckResult, AuditReport, AuditStatus
from blackjack_simulator.statistics.report import SimulationReport
from blackjack_simulator.trace import TraceEvent, TraceEventType


@dataclass(frozen=True, slots=True)
class AuditInput:
    report: SimulationReport
    trace_events: tuple[TraceEvent, ...]
    expected_rounds: int
    deterministic: bool


def build_audit_report(audit_input: AuditInput) -> AuditReport:
    return AuditReport(
        checks=(
            _check_round_count(audit_input.report, audit_input.expected_rounds),
            _check_sample_size(audit_input.expected_rounds),
            _check_bankroll_consistency(audit_input.report),
            _check_trace_sequence(audit_input.trace_events),
            _check_initial_bets(audit_input.trace_events, audit_input.expected_rounds),
            _check_card_deals(audit_input.trace_events),
            _check_strategy_actions_legal(audit_input.trace_events),
            _check_determinism(audit_input.deterministic),
            _skipped_card_identity_check(),
        ),
    )


def _check_sample_size(expected_rounds: int) -> AuditCheckResult:
    if expected_rounds >= 100:
        return AuditCheckResult(
            name="audit.sample_size",
            status=AuditStatus.PASS,
            description="Audit sample size is large enough for smoke validation.",
            details={"rounds": expected_rounds},
        )
    return AuditCheckResult(
        name="audit.sample_size",
        status=AuditStatus.WARNING,
        description="Audit sample is small; use more rounds for stronger coverage.",
        details={"rounds": expected_rounds, "recommended_minimum": 100},
    )


def _check_round_count(
    report: SimulationReport,
    expected_rounds: int,
) -> AuditCheckResult:
    if report.rounds == expected_rounds:
        return AuditCheckResult(
            name="statistics.round_count",
            status=AuditStatus.PASS,
            description="Statistics report round count matches requested rounds.",
            details={"rounds": report.rounds},
        )
    return AuditCheckResult(
        name="statistics.round_count",
        status=AuditStatus.FAIL,
        description="Statistics report round count does not match requested rounds.",
        details={"rounds": report.rounds, "expected_rounds": expected_rounds},
        violations=1,
    )


def _check_bankroll_consistency(report: SimulationReport) -> AuditCheckResult:
    expected = report.initial_bankroll + report.net_result
    if report.final_bankroll == expected:
        return AuditCheckResult(
            name="bankroll.final_balance",
            status=AuditStatus.PASS,
            description="Final bankroll equals initial bankroll plus net result.",
            details={"final_bankroll": report.final_bankroll},
        )
    return AuditCheckResult(
        name="bankroll.final_balance",
        status=AuditStatus.FAIL,
        description="Final bankroll does not equal initial bankroll plus net result.",
        details={
            "initial_bankroll": report.initial_bankroll,
            "net_result": report.net_result,
            "final_bankroll": report.final_bankroll,
            "expected_final_bankroll": expected,
        },
        violations=1,
    )


def _check_trace_sequence(events: tuple[TraceEvent, ...]) -> AuditCheckResult:
    expected = tuple(range(1, len(events) + 1))
    actual = tuple(event.sequence for event in events)
    if actual == expected:
        return AuditCheckResult(
            name="trace.sequence",
            status=AuditStatus.PASS,
            description="Trace event sequence is contiguous and ordered.",
            details={"events": len(events)},
        )
    return AuditCheckResult(
        name="trace.sequence",
        status=AuditStatus.FAIL,
        description="Trace event sequence is not contiguous.",
        details={"expected": expected[:10], "actual": actual[:10]},
        violations=1,
    )


def _check_initial_bets(
    events: tuple[TraceEvent, ...],
    expected_rounds: int,
) -> AuditCheckResult:
    rounds = {
        event.round_number
        for event in events
        if event.event_type is TraceEventType.INITIAL_BET_PLACED
    }
    if len(rounds) == expected_rounds:
        return AuditCheckResult(
            name="trace.initial_bets",
            status=AuditStatus.PASS,
            description="Each round has one initial betting event.",
            details={"initial_bet_rounds": len(rounds)},
        )
    missing = tuple(
        round_number
        for round_number in range(1, expected_rounds + 1)
        if round_number not in rounds
    )
    return AuditCheckResult(
        name="trace.initial_bets",
        status=AuditStatus.FAIL,
        description="At least one round is missing an initial betting event.",
        details={"initial_bet_rounds": len(rounds), "expected_rounds": expected_rounds},
        violations=len(missing),
        example_rounds=missing[:5],
    )


def _check_card_deals(events: tuple[TraceEvent, ...]) -> AuditCheckResult:
    violations = tuple(
        event.round_number
        for event in events
        if event.event_type is TraceEventType.CARD_DEALT
        and not isinstance(event.details.get("card"), str)
    )
    if not violations:
        return AuditCheckResult(
            name="trace.card_deals",
            status=AuditStatus.PASS,
            description="Card deal events include card identity.",
            details={
                "card_deal_events": sum(
                    event.event_type is TraceEventType.CARD_DEALT for event in events
                ),
            },
        )
    return AuditCheckResult(
        name="trace.card_deals",
        status=AuditStatus.FAIL,
        description="Some card deal events are missing card identity.",
        violations=len(violations),
        example_rounds=violations[:5],
    )


def _check_strategy_actions_legal(events: tuple[TraceEvent, ...]) -> AuditCheckResult:
    requested_actions: dict[tuple[int, str | None], list[set[str]]] = {}
    violations: list[int] = []
    for event in events:
        key = (event.round_number, event.hand_id)
        if event.event_type is TraceEventType.STRATEGY_DECISION_REQUESTED:
            legal_actions = event.details.get("legal_actions")
            if isinstance(legal_actions, list):
                requested_actions.setdefault(key, []).append(
                    {str(action) for action in legal_actions},
                )
            continue
        if event.event_type is not TraceEventType.STRATEGY_DECISION_RESOLVED:
            continue
        executed_action = event.details.get("executed_action")
        legal_action_sets = requested_actions.get(key, [])
        resolved_legal_actions: set[str] = (
            legal_action_sets.pop(0) if legal_action_sets else set()
        )
        if (
            not isinstance(executed_action, str)
            or executed_action not in resolved_legal_actions
        ):
            violations.append(event.round_number)

    if not violations:
        return AuditCheckResult(
            name="actions.legal",
            status=AuditStatus.PASS,
            description="Resolved strategy actions are present in legal actions.",
        )
    return AuditCheckResult(
        name="actions.legal",
        status=AuditStatus.FAIL,
        description="A resolved strategy action was not legal.",
        violations=len(violations),
        example_rounds=tuple(violations[:5]),
    )


def _check_determinism(deterministic: bool) -> AuditCheckResult:
    if deterministic:
        return AuditCheckResult(
            name="determinism.repeat_run",
            status=AuditStatus.PASS,
            description="Repeated run produced identical report and trace.",
        )
    return AuditCheckResult(
        name="determinism.repeat_run",
        status=AuditStatus.FAIL,
        description="Repeated run produced different report or trace.",
        violations=1,
    )


def _skipped_card_identity_check() -> AuditCheckResult:
    return AuditCheckResult(
        name="cards.unique_identity",
        status=AuditStatus.SKIPPED,
        description=(
            "Rank-only cards do not expose per-card identity yet; duplicate physical "
            "card detection requires a future shoe identity extension."
        ),
    )


def injected_bankroll_violation_report() -> AuditReport:
    report = SimulationReport(
        rounds=1,
        hands=1,
        initial_bankroll=Decimal("100"),
        final_bankroll=Decimal("999"),
        net_result=Decimal("10"),
        total_initial_bet=Decimal("10"),
        total_action=Decimal("10"),
        average_net_result=Decimal("10"),
        sample_variance=Decimal("0"),
        population_variance=Decimal("0"),
        house_edge_initial_bet=Decimal("-1"),
        house_edge_total_action=Decimal("-1"),
        rtp=Decimal("2"),
        max_drawdown=Decimal("0"),
        longest_win_streak=1,
        longest_loss_streak=0,
        longest_push_streak=0,
    )
    return build_audit_report(
        AuditInput(
            report=report,
            trace_events=(),
            expected_rounds=1,
            deterministic=True,
        ),
    )

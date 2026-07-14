"""Trace event output helpers."""

import json
from collections.abc import Iterable

from blackjack_simulator.trace import TraceEvent, TraceEventType


def trace_events_to_json(events: Iterable[TraceEvent]) -> str:
    return json.dumps([event.to_dict() for event in events], indent=2)


def render_trace_report(events: Iterable[TraceEvent]) -> str:
    lines: list[str] = []
    current_round: int | None = None
    for event in events:
        if event.round_number != current_round:
            current_round = event.round_number
            if lines:
                lines.append("")
            lines.append(f"Round {event.round_number}")
        hand = f" [{event.hand_id}]" if event.hand_id is not None else ""
        summary = _event_summary(event)
        lines.append(f"  #{event.sequence} {event.event_type.value}{hand}: {summary}")

    return "\n".join(lines)


def filter_trace_events(
    events: Iterable[TraceEvent],
    *,
    event_types: frozenset[TraceEventType] = frozenset(),
    feature_filters: frozenset[str] = frozenset(),
) -> list[TraceEvent]:
    filtered = list(events)
    if feature_filters:
        matching_rounds = {
            event.round_number
            for event in filtered
            if _event_matches_features(event, feature_filters)
        }
        filtered = [
            event for event in filtered if event.round_number in matching_rounds
        ]
    if event_types:
        filtered = [event for event in filtered if event.event_type in event_types]
    return filtered


def _event_matches_features(
    event: TraceEvent,
    feature_filters: frozenset[str],
) -> bool:
    if "split" in feature_filters and event.event_type is TraceEventType.PLAYER_SPLIT:
        return True
    if (
        "double" in feature_filters
        and event.event_type is TraceEventType.PLAYER_DOUBLED
    ):
        return True
    if (
        "surrender" in feature_filters
        and event.event_type is TraceEventType.PLAYER_SURRENDERED
    ):
        return True
    if "insurance" in feature_filters and (
        event.event_type is TraceEventType.INSURANCE_SETTLED
    ):
        return True
    return "blackjack" in feature_filters and event.details.get("outcome") in {
        "player_blackjack",
        "dealer_blackjack",
    }


def _event_summary(event: TraceEvent) -> str:
    if not event.details:
        return "-"

    return ", ".join(f"{key}={value}" for key, value in sorted(event.details.items()))

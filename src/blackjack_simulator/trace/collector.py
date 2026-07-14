"""In-memory trace event collector."""

from dataclasses import dataclass, field

from blackjack_simulator.trace.events import TraceEvent, TraceEventType, TraceValue


@dataclass(slots=True)
class TraceCollector:
    events: list[TraceEvent] = field(default_factory=list)
    _next_sequence: int = 1

    def record(
        self,
        event_type: TraceEventType,
        *,
        round_number: int,
        hand_id: str | None = None,
        details: dict[str, TraceValue] | None = None,
    ) -> TraceEvent:
        event = TraceEvent(
            event_type=event_type,
            sequence=self._next_sequence,
            round_number=round_number,
            hand_id=hand_id,
            details=details or {},
        )
        self.events.append(event)
        self._next_sequence += 1
        return event

    def to_dicts(self) -> list[dict[str, object]]:
        return [event.to_dict() for event in self.events]

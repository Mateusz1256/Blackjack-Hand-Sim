"""Typed trace event model."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Any


class TraceEventType(StrEnum):
    ROUND_STARTED = "round_started"
    INITIAL_BET_PLACED = "initial_bet_placed"
    CARD_DEALT = "card_dealt"
    STRATEGY_DECISION_REQUESTED = "strategy_decision_requested"
    STRATEGY_DECISION_RESOLVED = "strategy_decision_resolved"
    PLAYER_HIT = "player_hit"
    PLAYER_STOOD = "player_stood"
    PLAYER_DOUBLED = "player_doubled"
    PLAYER_SPLIT = "player_split"
    PLAYER_SURRENDERED = "player_surrendered"
    DEALER_HIT = "dealer_hit"
    HAND_SETTLED = "hand_settled"
    INSURANCE_SETTLED = "insurance_settled"
    ROUND_SETTLED = "round_settled"
    SHOE_SHUFFLED = "shoe_shuffled"


TraceValue = (
    str | int | bool | None | Decimal | list["TraceValue"] | dict[str, "TraceValue"]
)


@dataclass(frozen=True, slots=True)
class TraceEvent:
    event_type: TraceEventType
    sequence: int
    round_number: int
    hand_id: str | None = None
    details: dict[str, TraceValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.event_type.value,
            "sequence": self.sequence,
            "round_number": self.round_number,
            "hand_id": self.hand_id,
            "details": _json_value(self.details),
        }


def _json_value(value: TraceValue) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value

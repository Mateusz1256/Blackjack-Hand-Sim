"""JSON report output."""

import json
from decimal import Decimal
from typing import Any

from blackjack_simulator.statistics.report import SimulationReport


def report_to_json(report: SimulationReport) -> str:
    return json.dumps(report.to_dict(), default=_json_default, indent=2)


def _json_default(value: Any) -> str:
    if isinstance(value, Decimal):
        return str(value)

    msg = f"object of type {type(value).__name__} is not JSON serializable"
    raise TypeError(msg)

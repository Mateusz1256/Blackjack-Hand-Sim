"""Comparison report output helpers."""

import csv
import json
from decimal import Decimal
from io import StringIO
from typing import Any

from blackjack_simulator.comparison import ComparisonReport

_CSV_FIELDS = [
    "name",
    "config_path",
    "rounds",
    "hands",
    "net_result",
    "final_bankroll",
    "house_edge_initial_bet",
    "house_edge_total_action",
    "rtp",
    "average_net_result",
    "delta_net_result",
    "delta_house_edge_initial_bet",
    "delta_house_edge_total_action",
    "delta_rtp",
    "delta_average_net_result",
    "max_drawdown",
]


def render_comparison_report(report: ComparisonReport) -> str:
    lines = [
        f"Comparison mode: {report.mode.value}",
        f"Baseline: {report.baseline}",
    ]
    for note in report.notes:
        lines.append(f"Note: {note}")
    lines.append("")
    header = (
        "config | rounds | net | house_edge_initial | rtp | "
        "delta_house_edge_initial | delta_rtp"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for result in report.results:
        lines.append(
            f"{result.name} | {result.report.rounds} | {result.report.net_result} | "
            f"{result.report.house_edge_initial_bet} | {result.report.rtp} | "
            f"{result.delta_house_edge_initial_bet} | {result.delta_rtp}",
        )
    return "\n".join(lines)


def comparison_to_json(report: ComparisonReport) -> str:
    return json.dumps(report.to_dict(), default=_json_default, indent=2)


def comparison_to_csv(report: ComparisonReport) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=_CSV_FIELDS)
    writer.writeheader()
    for result in report.results:
        row = result.to_dict()
        writer.writerow({field: row[field] for field in _CSV_FIELDS})
    return output.getvalue()


def _json_default(value: Any) -> str:
    if isinstance(value, Decimal):
        return str(value)
    msg = f"object of type {type(value).__name__} is not JSON serializable"
    raise TypeError(msg)

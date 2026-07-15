"""Batch report output helpers."""

import csv
import json
from decimal import Decimal
from io import StringIO
from typing import Any

from blackjack_simulator.batch import BatchReport

_CSV_FIELDS = [
    "session_index",
    "seed",
    "rounds_completed",
    "initial_bankroll",
    "final_bankroll",
    "net_result",
    "max_drawdown",
    "ruined",
]


def render_batch_report(report: BatchReport) -> str:
    lines = [
        "Batch report",
        f"Sessions: {report.sessions_completed}",
        f"Rounds per session: {report.config.rounds_per_session}",
        f"Base seed: {report.config.base_seed}",
        f"Risk of ruin: {report.risk_of_ruin}",
        f"Ruin count: {report.ruin_count}",
        f"Profit rate: {report.profit_rate}",
        f"Loss rate: {report.loss_rate}",
        f"Final bankroll avg/median: "
        f"{report.average_final_bankroll} / {report.median_final_bankroll}",
        f"Final bankroll min/max: "
        f"{report.min_final_bankroll} / {report.max_final_bankroll}",
        f"Max drawdown avg/median: "
        f"{report.average_max_drawdown} / {report.median_max_drawdown}",
        "",
        "Final bankroll percentiles:",
    ]
    for percentile, value in report.percentile_final_bankrolls.items():
        lines.append(f"  p{percentile}: {value}")
    lines.append("")
    lines.append("Max drawdown percentiles:")
    for percentile, value in report.percentile_max_drawdowns.items():
        lines.append(f"  p{percentile}: {value}")
    return "\n".join(lines)


def batch_to_json(report: BatchReport) -> str:
    return json.dumps(report.to_dict(), default=_json_default, indent=2)


def batch_to_csv(report: BatchReport) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=_CSV_FIELDS)
    writer.writeheader()
    for result in report.session_results:
        row = result.to_dict()
        writer.writerow({field: row[field] for field in _CSV_FIELDS})
    return output.getvalue()


def _json_default(value: Any) -> str:
    if isinstance(value, Decimal):
        return str(value)
    msg = f"object of type {type(value).__name__} is not JSON serializable"
    raise TypeError(msg)

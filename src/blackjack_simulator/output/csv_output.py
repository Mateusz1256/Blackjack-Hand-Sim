"""CSV report output."""

import csv
from io import StringIO

from blackjack_simulator.statistics.report import SimulationReport

_CSV_FIELDS = [
    "rounds",
    "hands",
    "net_result",
    "initial_bankroll",
    "final_bankroll",
    "total_initial_bet",
    "total_action",
    "average_net_result",
    "sample_variance",
    "population_variance",
    "house_edge_initial_bet",
    "house_edge_total_action",
    "rtp",
    "max_drawdown",
    "longest_win_streak",
    "longest_loss_streak",
    "longest_push_streak",
]


def report_to_csv(report: SimulationReport) -> str:
    output = StringIO()
    row = report.to_dict()
    writer = csv.DictWriter(output, fieldnames=_CSV_FIELDS)
    writer.writeheader()
    writer.writerow(row)
    return output.getvalue()

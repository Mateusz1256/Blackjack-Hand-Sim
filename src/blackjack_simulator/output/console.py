"""Plain text report output."""

from blackjack_simulator.statistics.report import SimulationReport


def render_console_report(report: SimulationReport) -> str:
    return "\n".join(
        [
            f"Rounds: {report.rounds}",
            f"Hands: {report.hands}",
            f"Net result: {report.net_result}",
            f"Final bankroll: {report.final_bankroll}",
            f"House edge (initial bet): {report.house_edge_initial_bet}",
            f"House edge (total action): {report.house_edge_total_action}",
            f"RTP: {report.rtp}",
            f"Max drawdown: {report.max_drawdown}",
        ],
    )

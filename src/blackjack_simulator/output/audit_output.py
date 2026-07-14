"""Audit report output helpers."""

from blackjack_simulator.audit import AuditReport


def render_audit_report(report: AuditReport) -> str:
    lines = ["Audit report"]
    summary = report.to_dict()["summary"]
    lines.append(
        "Summary: "
        f"PASS={summary['passed']} "
        f"WARNING={summary['warnings']} "
        f"FAIL={summary['failed']} "
        f"SKIPPED={summary['skipped']}",
    )
    for check in report.checks:
        lines.append(f"{check.status.value} {check.name}: {check.description}")
        if check.violations:
            lines.append(f"  violations={check.violations}")
        if check.example_rounds:
            rounds = ", ".join(
                str(round_number) for round_number in check.example_rounds
            )
            lines.append(f"  example_rounds={rounds}")
    return "\n".join(lines)

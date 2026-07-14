from blackjack_simulator.audit import AuditStatus, run_config_audit
from blackjack_simulator.audit.checks import injected_bankroll_violation_report
from blackjack_simulator.configuration import parse_app_config


def audit_config_text(rounds: int = 100) -> str:
    return f"""
simulation:
  rounds: {rounds}
  seed: 123
  workers: 1
bankroll:
  initial: 100000
player:
  betting_strategy:
    type: flat
    amount: 10
  playing_strategy:
    type: basic_strategy
  insurance_strategy:
    type: never
rules:
  decks: 1
  penetration: 0.75
  blackjack_payout: 1.5
  dealer:
    hits_soft_17: false
    peeks_for_blackjack: true
output:
  console: true
"""


def test_config_audit_passes_core_invariants() -> None:
    report = run_config_audit(parse_app_config(audit_config_text()))

    statuses = {check.name: check.status for check in report.checks}
    assert statuses["statistics.round_count"] is AuditStatus.PASS
    assert statuses["bankroll.final_balance"] is AuditStatus.PASS
    assert statuses["actions.legal"] is AuditStatus.PASS
    assert statuses["determinism.repeat_run"] is AuditStatus.PASS
    assert not report.has_failures


def test_audit_identifies_injected_bankroll_violation() -> None:
    report = injected_bankroll_violation_report()

    failures = [check for check in report.checks if check.status is AuditStatus.FAIL]
    assert any(check.name == "bankroll.final_balance" for check in failures)
    assert report.exit_code(strict=False) == 1


def test_audit_strict_mode_fails_on_warning() -> None:
    report = run_config_audit(parse_app_config(audit_config_text(rounds=1)))

    assert report.has_warnings
    assert report.exit_code(strict=False) == 0
    assert report.exit_code(strict=True) == 1

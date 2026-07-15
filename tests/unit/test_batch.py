from decimal import Decimal
from pathlib import Path

import pytest

from blackjack_simulator.batch import (
    BatchConfig,
    BatchSessionResult,
    build_batch_report,
    derive_session_seed,
    percentile_nearest_rank,
    run_batch,
)
from blackjack_simulator.configuration import load_app_config

CONFIG = """
simulation:
  rounds: 2
  seed: 123
  workers: 1
bankroll:
  initial: 100
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


def write_config(tmp_path: Path) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(CONFIG, encoding="utf-8")
    return path


def session_result(
    *,
    index: int,
    final_bankroll: Decimal,
    max_drawdown: Decimal = Decimal("0"),
    ruined: bool = False,
) -> BatchSessionResult:
    return BatchSessionResult(
        session_index=index,
        seed=derive_session_seed(99, index),
        rounds_completed=10,
        initial_bankroll=Decimal("100"),
        final_bankroll=final_bankroll,
        net_result=final_bankroll - Decimal("100"),
        max_drawdown=max_drawdown,
        ruined=ruined,
    )


def test_derive_session_seed_is_deterministic_and_unique() -> None:
    assert derive_session_seed(123, 0) == derive_session_seed(123, 0)
    assert derive_session_seed(123, 0) != derive_session_seed(123, 1)
    with pytest.raises(ValueError, match="session index"):
        derive_session_seed(123, -1)


def test_percentile_nearest_rank() -> None:
    values = [Decimal("30"), Decimal("10"), Decimal("20"), Decimal("40")]

    assert percentile_nearest_rank(values, 0) == Decimal("10")
    assert percentile_nearest_rank(values, 50) == Decimal("20")
    assert percentile_nearest_rank(values, 95) == Decimal("40")
    assert percentile_nearest_rank(values, 100) == Decimal("40")


def test_build_batch_report_counts_ruin_and_profit_rates() -> None:
    report = build_batch_report(
        BatchConfig(sessions=3, rounds_per_session=10, base_seed=99),
        [
            session_result(index=0, final_bankroll=Decimal("120")),
            session_result(index=1, final_bankroll=Decimal("80"), ruined=True),
            session_result(index=2, final_bankroll=Decimal("100")),
        ],
    )

    assert report.sessions_completed == 3
    assert report.ruin_count == 1
    assert report.risk_of_ruin == Decimal("1") / Decimal("3")
    assert report.profitable_sessions == 1
    assert report.losing_sessions == 1
    assert report.breakeven_sessions == 1
    assert report.median_final_bankroll == Decimal("100")


def test_run_batch_is_deterministic_for_fixed_base_seed(tmp_path: Path) -> None:
    app_config = load_app_config(write_config(tmp_path))
    batch_config = BatchConfig(sessions=3, rounds_per_session=5, base_seed=777)

    first = run_batch(app_config, batch_config)
    second = run_batch(app_config, batch_config)

    assert first.to_dict() == second.to_dict()
    assert first.sessions_completed == 3
    assert set(first.percentile_final_bankrolls) == {5, 25, 50, 75, 95}

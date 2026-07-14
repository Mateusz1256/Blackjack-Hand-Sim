from pathlib import Path

from blackjack_simulator.cli.main import main
from blackjack_simulator.comparison import ComparisonMode, compare_configurations
from blackjack_simulator.output.comparison_output import (
    comparison_to_csv,
    comparison_to_json,
)

CONFIG_TEMPLATE = """
simulation:
  rounds: 5
  seed: 123
  workers: 1
bankroll:
  initial: 1000
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
  blackjack_payout: {payout}
  dealer:
    hits_soft_17: {hits_soft_17}
    peeks_for_blackjack: true
output:
  console: true
"""


def write_config(tmp_path: Path, name: str, payout: str, h17: bool = False) -> Path:
    path = tmp_path / name
    path.write_text(
        CONFIG_TEMPLATE.format(
            payout=payout,
            hits_soft_17=str(h17).lower(),
        ),
        encoding="utf-8",
    )
    return path


def test_compare_configurations_returns_baseline_deltas(tmp_path: Path) -> None:
    baseline = write_config(tmp_path, "s17.yaml", "1.5")
    variant = write_config(tmp_path, "six_to_five.yaml", "1.2", h17=True)

    report = compare_configurations(
        [baseline, variant],
        overrides={"rounds": 10, "seed": 99},
        mode=ComparisonMode.COMMON_RANDOM_NUMBERS,
    )

    assert report.baseline == "s17.yaml"
    assert len(report.results) == 2
    assert report.results[0].delta_net_result == 0
    assert report.results[0].delta_rtp == 0
    assert "Common random numbers" in report.notes[0]


def test_comparison_exports_json_and_csv(tmp_path: Path) -> None:
    baseline = write_config(tmp_path, "s17.yaml", "1.5")
    variant = write_config(tmp_path, "six_to_five.yaml", "1.2")
    report = compare_configurations([baseline, variant], overrides={"rounds": 3})

    json_payload = comparison_to_json(report)
    csv_payload = comparison_to_csv(report)

    assert '"baseline": "s17.yaml"' in json_payload
    assert "delta_house_edge_initial_bet" in csv_payload.splitlines()[0]
    assert "six_to_five" in csv_payload


def test_cli_compare_smoke(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    baseline = write_config(tmp_path, "s17.yaml", "1.5")
    variant = write_config(tmp_path, "six_to_five.yaml", "1.2")
    json_path = tmp_path / "comparison.json"
    csv_path = tmp_path / "comparison.csv"

    exit_code = main(
        [
            "compare",
            str(baseline),
            str(variant),
            "--rounds",
            "3",
            "--seed",
            "42",
            "--json-file",
            str(json_path),
            "--csv-file",
            str(csv_path),
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Comparison mode" in output
    assert "delta_house_edge_initial" in output
    assert json_path.exists()
    assert csv_path.exists()

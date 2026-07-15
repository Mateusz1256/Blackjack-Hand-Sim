from pathlib import Path

from blackjack_simulator.cli.main import main

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


def test_cli_validate_smoke(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)

    exit_code = main(["validate", str(config_path)])

    assert exit_code == 0
    assert "Configuration is valid" in capsys.readouterr().out


def test_cli_run_smoke(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)

    exit_code = main(["run", str(config_path), "--rounds", "1"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Rounds: 1" in output


def test_cli_run_accepts_worker_override(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)

    exit_code = main(["run", str(config_path), "--rounds", "1", "--workers", "1"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Rounds: 1" in output


def test_cli_trace_smoke(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)

    exit_code = main(["trace", str(config_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Round 1" in output
    assert "round_started" in output
    assert "card_dealt" in output


def test_cli_trace_writes_json(tmp_path: Path) -> None:
    config_path = write_config(tmp_path)
    output_path = tmp_path / "trace.json"

    exit_code = main(["trace", str(config_path), "--json-file", str(output_path)])

    payload = output_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert '"type": "round_started"' in payload
    assert '"round_number": 1' in payload


def test_cli_trace_filters_event_type(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)

    exit_code = main(
        [
            "trace",
            str(config_path),
            "--event-type",
            "round_settled",
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "round_settled" in output
    assert "card_dealt" not in output


def test_cli_invalid_config_returns_error(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "invalid.yaml"
    path.write_text("simulation:\n  rounds: 0\n", encoding="utf-8")

    exit_code = main(["validate", str(path)])

    assert exit_code == 2
    assert "simulation.rounds" in capsys.readouterr().err


def test_cli_audit_smoke(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)

    exit_code = main(["audit", str(config_path), "--rounds", "100"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Audit report" in output
    assert "PASS bankroll.final_balance" in output


def test_cli_audit_strict_fails_on_warning(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)

    exit_code = main(["audit", str(config_path), "--rounds", "1", "--strict"])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "WARNING audit.sample_size" in output


def test_cli_batch_smoke(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    config_path = write_config(tmp_path)
    json_path = tmp_path / "batch.json"
    csv_path = tmp_path / "batch.csv"

    exit_code = main(
        [
            "batch",
            str(config_path),
            "--sessions",
            "2",
            "--rounds-per-session",
            "3",
            "--base-seed",
            "42",
            "--json-file",
            str(json_path),
            "--csv-file",
            str(csv_path),
        ],
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Batch report" in output
    assert "Risk of ruin" in output
    assert json_path.exists()
    assert csv_path.exists()


def test_cli_presets_list_and_export(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    export_path = tmp_path / "standard.yaml"

    list_exit_code = main(["presets", "list"])
    list_output = capsys.readouterr().out
    export_exit_code = main(
        ["presets", "export", "standard-6d-s17", str(export_path)],
    )
    validate_exit_code = main(["presets", "validate", str(export_path)])

    assert list_exit_code == 0
    assert "standard-6d-s17" in list_output
    assert export_exit_code == 0
    assert validate_exit_code == 0

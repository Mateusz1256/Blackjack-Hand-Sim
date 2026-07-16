"""Comparison and batch worker tasks."""

import json
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from blackjack_api.workers.task_queue import CancellationToken, ProgressReporter
from blackjack_simulator.batch import BatchConfig, run_batch
from blackjack_simulator.comparison import ComparisonMode, compare_configurations
from blackjack_simulator.configuration import parse_app_config
from blackjack_simulator.output.batch_output import batch_to_csv, batch_to_json
from blackjack_simulator.output.comparison_output import (
    comparison_to_csv,
    comparison_to_json,
)

QueuedAnalysisTask = Callable[[ProgressReporter, CancellationToken], dict[str, Any]]


def comparison_task(
    configs: list[str],
    *,
    names: list[str] | None = None,
    mode: ComparisonMode = ComparisonMode.INDEPENDENT_SEEDS,
    overrides: dict[str, int] | None = None,
) -> QueuedAnalysisTask:
    def task(
        report_progress: ProgressReporter,
        cancellation: CancellationToken,
    ) -> dict[str, Any]:
        if len(configs) < 2:
            msg = "at least two configurations are required for comparison"
            raise ValueError(msg)
        report_progress(0, 2, "validating_configurations")
        for config_text in configs:
            cancellation.raise_if_cancelled()
            parse_app_config(config_text, overrides=overrides)

        report_progress(1, 2, "running_comparison")
        cancellation.raise_if_cancelled()
        with TemporaryDirectory() as tmpdir:
            paths = _write_temp_configs(Path(tmpdir), configs, names)
            report = compare_configurations(
                paths,
                overrides=overrides,
                mode=mode,
            )

        report_progress(2, 2, "completed")
        json_payload = comparison_to_json(report)
        return {
            "report": json.loads(json_payload),
            "json": json_payload,
            "csv": comparison_to_csv(report),
        }

    return task


def batch_task(
    config_text: str,
    *,
    sessions: int,
    rounds_per_session: int,
    base_seed: int | None = None,
) -> QueuedAnalysisTask:
    def task(
        report_progress: ProgressReporter,
        cancellation: CancellationToken,
    ) -> dict[str, Any]:
        report_progress(0, 2, "validating_configuration")
        app_config = parse_app_config(config_text)
        cancellation.raise_if_cancelled()
        report_progress(1, 2, "running_batch")
        resolved_base_seed = (
            base_seed if base_seed is not None else app_config.simulation.seed
        )
        report = run_batch(
            app_config,
            BatchConfig(
                sessions=sessions,
                rounds_per_session=rounds_per_session,
                base_seed=resolved_base_seed,
            ),
        )
        cancellation.raise_if_cancelled()
        report_progress(2, 2, "completed")
        json_payload = batch_to_json(report)
        return {
            "report": json.loads(json_payload),
            "json": json_payload,
            "csv": batch_to_csv(report),
        }

    return task


def _write_temp_configs(
    directory: Path,
    configs: list[str],
    names: list[str] | None,
) -> list[Path]:
    paths: list[Path] = []
    for index, config_text in enumerate(configs):
        name = (
            names[index]
            if names is not None and index < len(names)
            else f"config-{index}"
        )
        path = directory / f"{_safe_name(name)}.yaml"
        path.write_text(config_text, encoding="utf-8")
        paths.append(path)
    return paths


def _safe_name(name: str) -> str:
    safe = "".join(character if character.isalnum() else "-" for character in name)
    return safe.strip("-") or "config"

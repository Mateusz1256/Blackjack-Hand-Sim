"""Command line interface for blackjack simulator."""

import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path

from blackjack_simulator.audit import run_config_audit
from blackjack_simulator.batch import BatchConfig, run_batch
from blackjack_simulator.comparison import ComparisonMode, compare_configurations
from blackjack_simulator.configuration import ConfigurationError, load_app_config
from blackjack_simulator.engine import run_simulation, run_worker_simulations
from blackjack_simulator.output.audit_output import render_audit_report
from blackjack_simulator.output.batch_output import (
    batch_to_csv,
    batch_to_json,
    render_batch_report,
)
from blackjack_simulator.output.comparison_output import (
    comparison_to_csv,
    comparison_to_json,
    render_comparison_report,
)
from blackjack_simulator.output.console import render_console_report
from blackjack_simulator.output.csv_output import report_to_csv
from blackjack_simulator.output.json_output import report_to_json
from blackjack_simulator.output.trace_output import (
    filter_trace_events,
    render_trace_report,
    trace_events_to_json,
)
from blackjack_simulator.presets import (
    export_preset,
    get_builtin_preset,
    import_preset,
    list_builtin_presets,
    preset_to_yaml,
)
from blackjack_simulator.statistics.collector import StatisticsCollector
from blackjack_simulator.trace import TraceCollector, TraceEventType


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            return _validate(args)
        if args.command == "run":
            return _run(args)
        if args.command == "trace":
            return _trace(args)
        if args.command == "audit":
            return _audit(args)
        if args.command == "compare":
            return _compare(args)
        if args.command == "batch":
            return _batch(args)
        if args.command == "presets":
            return _presets(args)
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    parser.error("unknown command")
    return 2


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="blackjack-simulator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("validate", "run"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("config", type=Path)
        command_parser.add_argument("--rounds", type=int)
        command_parser.add_argument("--seed", type=int)
        command_parser.add_argument("--workers", type=int)

    trace_parser = subparsers.add_parser("trace")
    trace_parser.add_argument("config", type=Path)
    trace_parser.add_argument("--rounds", type=int)
    trace_parser.add_argument("--seed", type=int)
    trace_parser.add_argument("--workers", type=int)
    trace_parser.add_argument("--json-file", type=Path)
    trace_parser.add_argument(
        "--event-type",
        action="append",
        default=[],
        choices=[event_type.value for event_type in TraceEventType],
    )
    trace_parser.add_argument(
        "--only",
        action="append",
        default=[],
        choices=["split", "double", "surrender", "blackjack", "insurance"],
        help="Only show rounds containing the selected feature.",
    )

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("config", type=Path)
    audit_parser.add_argument("--rounds", type=int)
    audit_parser.add_argument("--seed", type=int)
    audit_parser.add_argument("--workers", type=int)
    audit_parser.add_argument("--strict", action="store_true")

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("configs", nargs="+", type=Path)
    compare_parser.add_argument("--rounds", type=int)
    compare_parser.add_argument("--seed", type=int)
    compare_parser.add_argument("--workers", type=int)
    compare_parser.add_argument(
        "--mode",
        choices=[mode.value for mode in ComparisonMode],
        default=ComparisonMode.INDEPENDENT_SEEDS.value,
    )
    compare_parser.add_argument("--json-file", type=Path)
    compare_parser.add_argument("--csv-file", type=Path)

    batch_parser = subparsers.add_parser("batch")
    batch_parser.add_argument("config", type=Path)
    batch_parser.add_argument("--sessions", type=int, required=True)
    batch_parser.add_argument("--rounds-per-session", type=int, required=True)
    batch_parser.add_argument("--base-seed", type=int)
    batch_parser.add_argument("--json-file", type=Path)
    batch_parser.add_argument("--csv-file", type=Path)

    presets_parser = subparsers.add_parser("presets")
    presets_subparsers = presets_parser.add_subparsers(
        dest="presets_command",
        required=True,
    )
    presets_subparsers.add_parser("list")

    presets_show_parser = presets_subparsers.add_parser("show")
    presets_show_parser.add_argument("preset_id")

    presets_export_parser = presets_subparsers.add_parser("export")
    presets_export_parser.add_argument("preset_id")
    presets_export_parser.add_argument("path", type=Path)

    presets_validate_parser = presets_subparsers.add_parser("validate")
    presets_validate_parser.add_argument("path", type=Path)

    return parser


def _validate(args: Namespace) -> int:
    load_app_config(args.config, overrides=_overrides(args))
    print("Configuration is valid")
    return 0


def _run(args: Namespace) -> int:
    app_config = load_app_config(args.config, overrides=_overrides(args))
    if app_config.simulation.workers > 1:
        result = run_worker_simulations(
            config=app_config.engine_config,
            shoe_config=app_config.create_worker_shoe_config(),
            top_level_seed=app_config.simulation.seed,
            worker_count=app_config.simulation.workers,
            player_strategy_factory=app_config.create_playing_strategy_factory(),
            insurance_strategy_factory=app_config.create_insurance_strategy_factory(),
            betting_strategy_factory=app_config.create_betting_strategy_factory(),
            card_counter_factory=app_config.create_card_counter_factory(),
        )
    else:
        collector = StatisticsCollector(
            initial_bankroll=app_config.engine_config.initial_bankroll,
        )
        shoe = app_config.create_shoe()
        card_counter = app_config.create_card_counter()
        result = run_simulation(
            shoe=shoe,
            config=app_config.engine_config,
            player_strategy=app_config.create_playing_strategy(shoe, card_counter),
            insurance_strategy=app_config.create_insurance_strategy(),
            betting_strategy=app_config.create_betting_strategy(shoe, card_counter),
            card_counter=card_counter,
            statistics_collector=collector,
            store_rounds=False,
        )
    report = result.statistics
    if report is None:
        return 1

    if app_config.output.console:
        print(render_console_report(report))
    if app_config.output.json_file is not None:
        Path(app_config.output.json_file).write_text(
            report_to_json(report),
            encoding="utf-8",
        )
    if app_config.output.csv_file is not None:
        Path(app_config.output.csv_file).write_text(
            report_to_csv(report),
            encoding="utf-8",
        )
    return 0


def _trace(args: Namespace) -> int:
    app_config = load_app_config(args.config, overrides=_overrides(args))
    shoe = app_config.create_shoe()
    card_counter = app_config.create_card_counter()
    trace_collector = TraceCollector()
    run_simulation(
        shoe=shoe,
        config=app_config.engine_config,
        player_strategy=app_config.create_playing_strategy(shoe, card_counter),
        insurance_strategy=app_config.create_insurance_strategy(),
        betting_strategy=app_config.create_betting_strategy(shoe, card_counter),
        card_counter=card_counter,
        store_rounds=False,
        trace_collector=trace_collector,
    )
    event_types = frozenset(
        TraceEventType(event_type) for event_type in args.event_type
    )
    feature_filters = frozenset(args.only)
    events = filter_trace_events(
        trace_collector.events,
        event_types=event_types,
        feature_filters=feature_filters,
    )
    if args.json_file is not None:
        args.json_file.write_text(trace_events_to_json(events), encoding="utf-8")
    print(render_trace_report(events))
    return 0


def _audit(args: Namespace) -> int:
    app_config = load_app_config(args.config, overrides=_overrides(args))
    report = run_config_audit(app_config)
    print(render_audit_report(report))
    return report.exit_code(strict=bool(args.strict))


def _compare(args: Namespace) -> int:
    try:
        report = compare_configurations(
            args.configs,
            overrides=_overrides(args),
            mode=ComparisonMode(args.mode),
        )
    except ValueError as exc:
        print(f"Comparison error: {exc}", file=sys.stderr)
        return 2
    if args.json_file is not None:
        args.json_file.write_text(comparison_to_json(report), encoding="utf-8")
    if args.csv_file is not None:
        args.csv_file.write_text(comparison_to_csv(report), encoding="utf-8")
    print(render_comparison_report(report))
    return 0


def _batch(args: Namespace) -> int:
    app_config = load_app_config(args.config)
    base_seed = (
        args.base_seed if args.base_seed is not None else app_config.simulation.seed
    )
    try:
        report = run_batch(
            app_config,
            BatchConfig(
                sessions=args.sessions,
                rounds_per_session=args.rounds_per_session,
                base_seed=base_seed,
            ),
        )
    except ValueError as exc:
        print(f"Batch error: {exc}", file=sys.stderr)
        return 2

    if args.json_file is not None:
        args.json_file.write_text(batch_to_json(report), encoding="utf-8")
    if args.csv_file is not None:
        args.csv_file.write_text(batch_to_csv(report), encoding="utf-8")
    print(render_batch_report(report))
    return 0


def _presets(args: Namespace) -> int:
    if args.presets_command == "list":
        for preset in list_builtin_presets():
            metadata = preset.metadata
            print(
                f"{metadata.id} | {metadata.name} | "
                f"{metadata.category} | {', '.join(metadata.tags)}",
            )
        return 0

    if args.presets_command == "show":
        try:
            preset = get_builtin_preset(args.preset_id)
        except KeyError as exc:
            print(f"Preset error: {exc}", file=sys.stderr)
            return 2
        print(preset_to_yaml(preset))
        return 0

    if args.presets_command == "export":
        try:
            preset = get_builtin_preset(args.preset_id)
        except KeyError as exc:
            print(f"Preset error: {exc}", file=sys.stderr)
            return 2
        export_preset(preset, args.path)
        print(f"Preset exported to {args.path}")
        return 0

    if args.presets_command == "validate":
        try:
            preset = import_preset(args.path)
        except ValueError as exc:
            print(f"Preset error: {exc}", file=sys.stderr)
            return 2
        print(f"Preset is valid: {preset.metadata.id}")
        return 0

    return 2


def _overrides(args: Namespace) -> dict[str, int]:
    overrides: dict[str, int] = {}
    if args.rounds is not None:
        overrides["rounds"] = args.rounds
    if args.seed is not None:
        overrides["seed"] = args.seed
    if args.workers is not None:
        overrides["workers"] = args.workers
    return overrides


if __name__ == "__main__":
    raise SystemExit(main())

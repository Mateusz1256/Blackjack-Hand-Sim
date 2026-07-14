"""Command line interface for blackjack simulator."""

import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path

from blackjack_simulator.configuration import ConfigurationError, load_app_config
from blackjack_simulator.engine import run_simulation, run_worker_simulations
from blackjack_simulator.output.console import render_console_report
from blackjack_simulator.output.csv_output import report_to_csv
from blackjack_simulator.output.json_output import report_to_json
from blackjack_simulator.statistics.collector import StatisticsCollector


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
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    parser.error("unknown command")
    return 2


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="blackjack-simulator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("validate", "run", "trace"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("config", type=Path)
        command_parser.add_argument("--rounds", type=int)
        command_parser.add_argument("--seed", type=int)
        command_parser.add_argument("--workers", type=int)

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
            player_strategy=app_config.create_playing_strategy(),
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
    result = run_simulation(
        shoe=shoe,
        config=app_config.engine_config,
        player_strategy=app_config.create_playing_strategy(),
        insurance_strategy=app_config.create_insurance_strategy(),
        betting_strategy=app_config.create_betting_strategy(shoe, card_counter),
        card_counter=card_counter,
    )
    for index, round_result in enumerate(result.rounds, start=1):
        print(
            f"Round {index}: net={round_result.net_result} "
            f"hands={len(round_result.player_hands)} "
            f"dealer={round_result.dealer_hand.value}",
        )
    return 0


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

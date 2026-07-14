from pathlib import Path

from blackjack_simulator.cli.main import main
from blackjack_simulator.configuration import load_app_config
from blackjack_simulator.engine import run_worker_simulations

CONFIG_DIR = Path(__file__).parents[2] / "configs"


def config_paths() -> list[Path]:
    return sorted(CONFIG_DIR.glob("*.yaml"))


def test_all_example_configurations_validate() -> None:
    paths = config_paths()

    assert paths
    for path in paths:
        assert main(["validate", str(path)]) == 0


def test_all_example_configurations_run_with_small_override() -> None:
    for path in config_paths():
        assert main(["run", str(path), "--rounds", "3", "--workers", "1"]) == 0


def test_million_round_configuration_worker_smoke_is_deterministic() -> None:
    app_config = load_app_config(
        CONFIG_DIR / "validation_1m.yaml",
        overrides={"rounds": 2000, "workers": 2},
    )

    first = run_worker_simulations(
        config=app_config.engine_config,
        shoe_config=app_config.create_worker_shoe_config(),
        top_level_seed=app_config.simulation.seed,
        worker_count=app_config.simulation.workers,
        player_strategy_factory=app_config.create_playing_strategy_factory(),
        insurance_strategy_factory=app_config.create_insurance_strategy_factory(),
        betting_strategy_factory=app_config.create_betting_strategy_factory(),
        use_processes=False,
    )
    second = run_worker_simulations(
        config=app_config.engine_config,
        shoe_config=app_config.create_worker_shoe_config(),
        top_level_seed=app_config.simulation.seed,
        worker_count=app_config.simulation.workers,
        player_strategy_factory=app_config.create_playing_strategy_factory(),
        insurance_strategy_factory=app_config.create_insurance_strategy_factory(),
        betting_strategy_factory=app_config.create_betting_strategy_factory(),
        use_processes=False,
    )

    assert first.statistics is not None
    assert second.statistics is not None
    assert first.statistics == second.statistics
    assert first.statistics.rounds == 2000

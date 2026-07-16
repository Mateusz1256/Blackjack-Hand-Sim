from pathlib import Path

import pytest

from blackjack_api.repositories import (
    ConfigurationRepository,
    PresetRepository,
    RunRepository,
)
from blackjack_api.repositories.migrations import SCHEMA_VERSION
from blackjack_api.services import open_database
from blackjack_simulator.configuration import parse_app_config
from blackjack_simulator.presets import get_builtin_preset

CONFIG_TEXT = """
simulation:
  rounds: 3
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


def database_path(tmp_path: Path) -> Path:
    return tmp_path / "blackjack-api.sqlite3"


def test_migration_smoke_sets_schema_version(tmp_path: Path) -> None:
    connection = open_database(database_path(tmp_path))

    version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert version == SCHEMA_VERSION


def test_configuration_repository_roundtrip_and_validation(tmp_path: Path) -> None:
    connection = open_database(database_path(tmp_path))
    repository = ConfigurationRepository(connection)

    created = repository.create(name="baseline", config_text=CONFIG_TEXT)
    loaded = repository.get(created.id)

    assert loaded == created
    assert loaded is not None
    assert parse_app_config(loaded.config_text).simulation.rounds == 3


def test_configuration_duplicate_and_delete_behavior(tmp_path: Path) -> None:
    connection = open_database(database_path(tmp_path))
    repository = ConfigurationRepository(connection)
    created = repository.create(name="baseline", config_text=CONFIG_TEXT)

    with pytest.raises(ValueError, match="already exists"):
        repository.create(name="baseline", config_text=CONFIG_TEXT)

    assert repository.delete(created.id) is True
    assert repository.delete(created.id) is False
    assert repository.get(created.id) is None


def test_run_repository_stores_reproducible_config_snapshot(tmp_path: Path) -> None:
    connection = open_database(database_path(tmp_path))
    configuration_repository = ConfigurationRepository(connection)
    run_repository = RunRepository(connection)
    configuration = configuration_repository.create(
        name="baseline",
        config_text=CONFIG_TEXT,
    )

    created = run_repository.create(
        configuration_id=configuration.id,
        run_type="simulation",
        status="completed",
        seed=123,
        rounds=3,
        config_snapshot=configuration.config_text,
        result={"final_bankroll": "110"},
    )
    loaded = run_repository.get(created.id)

    assert loaded == created
    assert loaded is not None
    assert loaded.result() == {"final_bankroll": "110"}
    assert parse_app_config(loaded.config_snapshot).simulation.seed == 123


def test_run_configuration_reference_is_preserved_as_snapshot_after_delete(
    tmp_path: Path,
) -> None:
    connection = open_database(database_path(tmp_path))
    configuration_repository = ConfigurationRepository(connection)
    run_repository = RunRepository(connection)
    configuration = configuration_repository.create(
        name="baseline",
        config_text=CONFIG_TEXT,
    )
    created = run_repository.create(
        configuration_id=configuration.id,
        run_type="simulation",
        status="queued",
        config_snapshot=configuration.config_text,
    )

    assert configuration_repository.delete(configuration.id) is True
    loaded = run_repository.get(created.id)

    assert loaded is not None
    assert loaded.configuration_id is None
    assert loaded.config_snapshot == CONFIG_TEXT


def test_preset_repository_roundtrip_and_read_only_delete(tmp_path: Path) -> None:
    connection = open_database(database_path(tmp_path))
    repository = PresetRepository(connection)
    preset = get_builtin_preset("standard-6d-s17")

    created = repository.upsert(preset)
    loaded = repository.get(preset.metadata.id)

    assert loaded == created
    assert loaded is not None
    assert loaded.metadata()["id"] == "standard-6d-s17"
    assert loaded.preset().to_dict() == preset.to_dict()
    with pytest.raises(ValueError, match="read-only preset"):
        repository.delete(preset.metadata.id)

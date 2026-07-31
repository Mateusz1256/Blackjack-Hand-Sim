from pathlib import Path

from fastapi.testclient import TestClient

from blackjack_api.config import BackendSettings
from blackjack_api.main import create_app

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


def test_presets_list_duplicate_export_and_guarded_delete(tmp_path: Path) -> None:
    client = TestClient(create_test_app(tmp_path))

    listed = client.get("/api/v1/presets")
    assert listed.status_code == 200
    preset_id = listed.json()["presets"][0]["id"]

    duplicate = client.post(
        f"/api/v1/presets/{preset_id}/duplicate",
        json={"id": "custom-copy", "name": "Custom Copy"},
    )
    assert duplicate.status_code == 201
    assert duplicate.json()["read_only"] is False

    exported = client.get("/api/v1/presets/custom-copy/export")
    assert exported.status_code == 200
    assert "metadata:" in exported.text

    guarded_delete = client.delete(f"/api/v1/presets/{preset_id}")
    assert guarded_delete.status_code == 409

    deleted = client.delete("/api/v1/presets/custom-copy")
    assert deleted.status_code == 204


def test_history_lists_filters_rerun_snapshot_and_deletes(tmp_path: Path) -> None:
    client = TestClient(create_test_app(tmp_path))

    job = client.post("/api/v1/simulations", json={"config_text": CONFIG_TEXT})
    assert job.status_code == 202

    history = client.get("/api/v1/history?run_type=simulation")
    assert history.status_code == 200
    runs = history.json()["runs"]
    assert len(runs) == 1
    assert runs[0]["config_snapshot"] == CONFIG_TEXT

    deleted = client.delete(f"/api/v1/history/{runs[0]['id']}")
    assert deleted.status_code == 204

    empty = client.get("/api/v1/history?run_type=simulation")
    assert empty.status_code == 200
    assert empty.json()["runs"] == []


def create_test_app(tmp_path: Path):
    return create_app(BackendSettings(database_path=str(tmp_path / "api.sqlite3")))

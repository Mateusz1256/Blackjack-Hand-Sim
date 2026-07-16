from time import sleep, time

from fastapi.testclient import TestClient

from blackjack_api.main import create_app

CONFIG_TEMPLATE = """
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
  blackjack_payout: {payout}
  dealer:
    hits_soft_17: {h17}
    peeks_for_blackjack: true
output:
  console: true
"""


def config_text(*, payout: str = "1.5", h17: bool = False) -> str:
    return CONFIG_TEMPLATE.format(payout=payout, h17=str(h17).lower())


def test_comparison_endpoint_smoke_and_exports() -> None:
    client = TestClient(create_app())

    start = client.post(
        "/api/v1/comparisons",
        json={
            "configs": [
                config_text(),
                config_text(payout="1.2", h17=True),
            ],
            "names": ["baseline", "variant"],
            "rounds": 2,
            "seed": 99,
        },
    )
    assert start.status_code == 202
    job_id = start.json()["job_id"]

    wait_for_completion(client, f"/api/v1/comparisons/{job_id}")

    result = client.get(f"/api/v1/comparisons/{job_id}/result")
    json_export = client.get(f"/api/v1/comparisons/{job_id}/export/json")
    csv_export = client.get(f"/api/v1/comparisons/{job_id}/export/csv")

    assert result.status_code == 200
    payload = result.json()["result"]["report"]
    assert payload["baseline"] == "baseline.yaml"
    assert len(payload["results"]) == 2
    assert json_export.status_code == 200
    assert json_export.headers["content-type"].startswith("application/json")
    assert csv_export.status_code == 200
    assert "delta_rtp" in csv_export.text.splitlines()[0]


def test_batch_endpoint_smoke_and_exports() -> None:
    client = TestClient(create_app())

    start = client.post(
        "/api/v1/batches",
        json={
            "config_text": config_text(),
            "sessions": 2,
            "rounds_per_session": 2,
            "base_seed": 42,
        },
    )
    assert start.status_code == 202
    job_id = start.json()["job_id"]

    wait_for_completion(client, f"/api/v1/batches/{job_id}")

    result = client.get(f"/api/v1/batches/{job_id}/result")
    json_export = client.get(f"/api/v1/batches/{job_id}/export/json")
    csv_export = client.get(f"/api/v1/batches/{job_id}/export/csv")

    assert result.status_code == 200
    payload = result.json()["result"]["report"]
    assert payload["sessions_completed"] == 2
    assert payload["config"]["rounds_per_session"] == 2
    assert json_export.status_code == 200
    assert csv_export.status_code == 200
    assert "session_index" in csv_export.text.splitlines()[0]


def test_comparison_requires_two_configs() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/comparisons",
        json={"configs": [config_text()]},
    )

    assert response.status_code == 422


def test_batch_validation_error_is_mapped() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/batches",
        json={
            "config_text": "simulation:\n  rounds: 0\n",
            "sessions": 1,
            "rounds_per_session": 1,
        },
    )

    assert response.status_code == 422
    assert "simulation.rounds" in response.json()["detail"]


def wait_for_completion(client: TestClient, path: str) -> None:
    deadline = time() + 5
    while time() < deadline:
        response = client.get(path)
        assert response.status_code == 200
        if response.json()["status"] == "completed":
            return
        sleep(0.01)
    raise AssertionError(f"job at {path} did not complete")

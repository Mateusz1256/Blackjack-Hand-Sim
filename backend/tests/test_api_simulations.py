from time import sleep, time
from typing import Any

from fastapi.testclient import TestClient

from blackjack_api.main import create_app
from blackjack_api.services import TaskService
from blackjack_api.workers import JobStatus, LocalTaskQueue
from blackjack_api.workers.task_queue import CancellationToken, ProgressReporter

CONFIG_TEXT = """
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


def test_validate_simulation_endpoint() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/simulations/validate",
        json={"config_text": CONFIG_TEXT},
    )

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "rounds": 2,
        "seed": 123,
        "workers": 1,
    }


def test_simulation_endpoint_happy_path_result_and_trace() -> None:
    app = create_app()
    client = TestClient(app)

    start = client.post("/api/v1/simulations", json={"config_text": CONFIG_TEXT})
    assert start.status_code == 202
    job_id = start.json()["job_id"]

    wait_for_completion(client, job_id)

    status_response = client.get(f"/api/v1/simulations/{job_id}")
    result_response = client.get(f"/api/v1/simulations/{job_id}/result")
    trace_response = client.get(f"/api/v1/simulations/{job_id}/trace")

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert result_response.status_code == 200
    result = result_response.json()["result"]
    assert result["report"]["rounds"] == 2
    assert result["report_json"].startswith("{")
    assert trace_response.status_code == 200
    assert trace_response.json()["events"][0]["type"] == "round_started"


def test_invalid_simulation_config_returns_422() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/simulations",
        json={"config_text": "simulation:\n  rounds: 0\n"},
    )

    assert response.status_code == 422
    assert "simulation.rounds" in response.json()["detail"]


def test_missing_job_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/simulations/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "job not found"


def test_failed_job_result_maps_to_conflict_without_traceback() -> None:
    app = create_app()
    queue = LocalTaskQueue()
    app.state.task_service = TaskService(queue=queue)
    client = TestClient(app)

    job = queue.enqueue(failing_task)
    wait_for_terminal_queue(queue, job.id)

    response = client.get(f"/api/v1/simulations/{job.id}/result")
    queue.shutdown()

    assert response.status_code == 409
    assert response.json()["detail"] == "controlled failure"


def test_cancel_endpoint_returns_current_job_status() -> None:
    app = create_app()
    queue = LocalTaskQueue()
    app.state.task_service = TaskService(queue=queue)
    client = TestClient(app)

    job = queue.enqueue(long_task)
    response = client.post(f"/api/v1/simulations/{job.id}/cancel")
    queue.shutdown()

    assert response.status_code == 200
    assert response.json()["status"] in {"cancelled", "completed"}


def wait_for_completion(client: TestClient, job_id: str) -> None:
    deadline = time() + 5
    while time() < deadline:
        response = client.get(f"/api/v1/simulations/{job_id}")
        assert response.status_code == 200
        if response.json()["status"] == "completed":
            return
        sleep(0.01)
    raise AssertionError(f"job {job_id} did not complete")


def wait_for_terminal_queue(queue: LocalTaskQueue, job_id: str) -> None:
    deadline = time() + 5
    terminal = {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}
    while time() < deadline:
        job = queue.get(job_id)
        if job is not None and job.status in terminal:
            return
        sleep(0.01)
    raise AssertionError(f"job {job_id} did not reach terminal status")


def failing_task(
    progress: ProgressReporter,
    token: CancellationToken,
) -> dict[str, Any]:
    del progress, token
    raise RuntimeError("controlled failure")


def long_task(
    progress: ProgressReporter,
    token: CancellationToken,
) -> dict[str, Any]:
    for index in range(10):
        if token.is_cancelled():
            return {}
        progress(index, 10, "running")
        sleep(0.01)
    return {}

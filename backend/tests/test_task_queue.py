from threading import Event
from time import sleep, time
from typing import Any

import pytest

from blackjack_api.services import TaskService
from blackjack_api.workers import JobStatus, LocalTaskQueue, TaskCancelledError
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


def wait_for_status(
    queue: LocalTaskQueue,
    job_id: str,
    *statuses: JobStatus,
) -> None:
    deadline = time() + 5
    while time() < deadline:
        job = queue.get(job_id)
        if job is not None and job.status in statuses:
            return
        sleep(0.01)
    job = queue.get(job_id)
    raise AssertionError(f"job did not reach {statuses}: {job}")


def test_job_lifecycle_completes_with_progress() -> None:
    queue = LocalTaskQueue()

    job = queue.enqueue(
        lambda progress, token: _successful_task(progress, token),
    )
    wait_for_status(queue, job.id, JobStatus.COMPLETED)
    completed = queue.get(job.id)
    queue.shutdown()

    assert completed is not None
    assert completed.status is JobStatus.COMPLETED
    assert completed.progress.current == completed.progress.total
    assert completed.result == {"ok": True}


def test_job_can_be_cancelled() -> None:
    queue = LocalTaskQueue()
    started = Event()

    def cancellable(
        progress: ProgressReporter,
        token: CancellationToken,
    ) -> dict[str, Any]:
        started.set()
        for index in range(50):
            token.raise_if_cancelled()
            progress(index, 50, "working")
            sleep(0.01)
        return {"done": True}

    job = queue.enqueue(cancellable)
    assert started.wait(timeout=2)

    assert queue.cancel(job.id) is True
    wait_for_status(queue, job.id, JobStatus.CANCELLED)
    cancelled = queue.get(job.id)
    queue.shutdown()

    assert cancelled is not None
    assert cancelled.status is JobStatus.CANCELLED


def test_job_failure_status_contains_error() -> None:
    queue = LocalTaskQueue()

    def failing(
        progress: ProgressReporter,
        token: CancellationToken,
    ) -> dict[str, Any]:
        del progress, token
        raise RuntimeError("boom")

    job = queue.enqueue(failing)
    wait_for_status(queue, job.id, JobStatus.FAILED)
    failed = queue.get(job.id)
    queue.shutdown()

    assert failed is not None
    assert failed.status is JobStatus.FAILED
    assert failed.error == "boom"


def test_task_service_enqueues_and_completes_short_simulation() -> None:
    queue = LocalTaskQueue()
    service = TaskService(queue=queue)

    job = service.enqueue_simulation(CONFIG_TEXT)
    wait_for_status(queue, job.id, JobStatus.COMPLETED)
    completed = service.get_job(job.id)
    queue.shutdown()

    assert completed is not None
    assert completed.status is JobStatus.COMPLETED
    assert completed.result is not None
    assert completed.result["report"]["rounds"] == 2
    assert service.cancel_job(job.id) is False


def test_progress_validation_rejects_unbounded_updates() -> None:
    queue = LocalTaskQueue()

    def invalid_progress(
        progress: ProgressReporter,
        token: CancellationToken,
    ) -> dict[str, Any]:
        del token
        progress(2, 1, "invalid")
        return {}

    job = queue.enqueue(invalid_progress)
    wait_for_status(queue, job.id, JobStatus.FAILED)
    failed = queue.get(job.id)
    queue.shutdown()

    assert failed is not None
    assert failed.status is JobStatus.FAILED
    assert "current must not exceed total" in str(failed.error)


def _successful_task(
    progress: ProgressReporter,
    token: CancellationToken,
) -> dict[str, Any]:
    progress(0, 1, "starting")
    token.raise_if_cancelled()
    progress(1, 1, "done")
    return {"ok": True}


def test_task_cancelled_exception_is_public() -> None:
    token = CancellationToken()
    token.cancel()
    with pytest.raises(TaskCancelledError):
        token.raise_if_cancelled()

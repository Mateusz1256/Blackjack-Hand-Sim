"""Local bounded-progress task queue."""

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from enum import StrEnum
from threading import Event, Lock
from typing import Any
from uuid import uuid4


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class JobProgress:
    current: int = 0
    total: int = 1
    message: str = "queued"

    def __post_init__(self) -> None:
        if self.current < 0:
            msg = "job progress current must not be negative"
            raise ValueError(msg)
        if self.total <= 0:
            msg = "job progress total must be positive"
            raise ValueError(msg)
        if self.current > self.total:
            msg = "job progress current must not exceed total"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    status: JobStatus
    progress: JobProgress = field(default_factory=JobProgress)
    result: dict[str, Any] | None = None
    error: str | None = None


class TaskCancelledError(Exception):
    """Raised by tasks when cancellation is observed."""


class CancellationToken:
    def __init__(self) -> None:
        self._event = Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def raise_if_cancelled(self) -> None:
        if self.is_cancelled():
            raise TaskCancelledError("job was cancelled")


ProgressReporter = Callable[[int, int, str], None]
QueuedTask = Callable[[ProgressReporter, CancellationToken], dict[str, Any]]


class LocalTaskQueue:
    def __init__(self, *, max_workers: int = 1) -> None:
        if max_workers <= 0:
            msg = "max workers must be positive"
            raise ValueError(msg)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = Lock()
        self._jobs: dict[str, Job] = {}
        self._tokens: dict[str, CancellationToken] = {}
        self._futures: dict[str, Future[None]] = {}

    def enqueue(self, task: QueuedTask) -> Job:
        job_id = str(uuid4())
        token = CancellationToken()
        job = Job(id=job_id, status=JobStatus.QUEUED)
        with self._lock:
            self._jobs[job_id] = job
            self._tokens[job_id] = token

        future = self._executor.submit(self._run_task, job_id, task, token)
        with self._lock:
            self._futures[job_id] = future
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            token = self._tokens.get(job_id)
            future = self._futures.get(job_id)
            if job is None or token is None:
                return False
            if job.status in {
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            }:
                return False
            token.cancel()
            if future is not None:
                future.cancel()
            self._jobs[job_id] = replace(
                job,
                status=JobStatus.CANCELLED,
                progress=JobProgress(
                    current=job.progress.current,
                    total=job.progress.total,
                    message="cancelled",
                ),
            )
            return True

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=True)

    def _run_task(
        self,
        job_id: str,
        task: QueuedTask,
        token: CancellationToken,
    ) -> None:
        self._set_status(job_id, JobStatus.RUNNING, message="running")
        try:
            token.raise_if_cancelled()
            result = task(
                lambda current, total, message: self._set_progress(
                    job_id,
                    current,
                    total,
                    message,
                ),
                token,
            )
        except TaskCancelledError as exc:
            self._set_status(job_id, JobStatus.CANCELLED, message=str(exc))
            return
        except Exception as exc:
            self._set_status(job_id, JobStatus.FAILED, message="failed", error=str(exc))
            return

        with self._lock:
            job = self._jobs[job_id]
            self._jobs[job_id] = replace(
                job,
                status=JobStatus.COMPLETED,
                progress=JobProgress(
                    current=job.progress.total,
                    total=job.progress.total,
                    message="completed",
                ),
                result=result,
                error=None,
            )

    def _set_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        message: str,
        error: str | None = None,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            self._jobs[job_id] = replace(
                job,
                status=status,
                progress=JobProgress(
                    current=job.progress.current,
                    total=job.progress.total,
                    message=message,
                ),
                error=error,
            )

    def _set_progress(
        self,
        job_id: str,
        current: int,
        total: int,
        message: str,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job.status is JobStatus.CANCELLED:
                raise TaskCancelledError("job was cancelled")
            self._jobs[job_id] = replace(
                job,
                progress=JobProgress(current=current, total=total, message=message),
            )

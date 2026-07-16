"""Shared job route helpers."""

from typing import Literal

from fastapi import HTTPException, Response, status

from blackjack_api.schemas.jobs import (
    JobProgressResponse,
    JobResponse,
    JobResultResponse,
)
from blackjack_api.services import TaskService
from blackjack_api.workers import Job, JobStatus


def require_job(task_service: TaskService, job_id: str) -> Job:
    job = task_service.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="job not found",
        )
    return job


def job_response(job: Job) -> JobResponse:
    return JobResponse(
        job_id=job.id,
        status=job.status.value,
        progress=JobProgressResponse(
            current=job.progress.current,
            total=job.progress.total,
            message=job.progress.message,
        ),
        error=job.error if job.status is JobStatus.FAILED else None,
    )


def completed_result_response(job: Job) -> JobResultResponse:
    if job.status is JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=job.error or "job failed",
        )
    if job.status is JobStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="job was cancelled",
        )
    if job.status is not JobStatus.COMPLETED or job.result is None:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="job is not complete",
        )
    return JobResultResponse(job_id=job.id, status=job.status.value, result=job.result)


def export_response(
    job: Job,
    export_format: Literal["json", "csv"],
) -> Response:
    completed = completed_result_response(job)
    payload = completed.result.get(export_format)
    if not isinstance(payload, str):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{export_format} export is not available",
        )
    media_type = "application/json" if export_format == "json" else "text/csv"
    return Response(content=payload, media_type=media_type)

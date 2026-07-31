"""Shared job route helpers."""

from fastapi import HTTPException, Response, status

from blackjack_api.schemas.jobs import (
    JobProgressResponse,
    JobResponse,
    JobResultResponse,
)
from blackjack_api.services import TaskService
from blackjack_api.services.export_service import (
    ExportFormat,
    ExportNotAvailableError,
    ExportService,
    ReportType,
)
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
    report_type: ReportType,
    export_format: ExportFormat,
) -> Response:
    completed = completed_result_response(job)
    try:
        content, media_type, filename = ExportService().export(
            job_id=job.id,
            report_type=report_type,
            result=completed.result,
            export_format=export_format,
        )
    except ExportNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

"""Batch simulation API routes."""

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Response, status

from blackjack_api.api.routes._jobs import (
    completed_result_response,
    export_response,
    job_response,
    require_job,
)
from blackjack_api.dependencies import get_task_service
from blackjack_api.schemas.analysis import BatchStartRequest
from blackjack_api.schemas.jobs import JobResponse, JobResultResponse
from blackjack_api.services import TaskService
from blackjack_api.services.export_service import ExportFormat
from blackjack_simulator.configuration import ConfigurationError

router = APIRouter(prefix="/batches")
TaskServiceDependency = Depends(get_task_service)
EXPORT_FORMATS = {"json", "csv", "zip", "pdf", "chart.svg"}


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def start_batch(
    request: BatchStartRequest,
    task_service: TaskService = TaskServiceDependency,
) -> JobResponse:
    try:
        job = task_service.enqueue_batch(
            request.config_text,
            sessions=request.sessions,
            rounds_per_session=request.rounds_per_session,
            base_seed=request.base_seed,
            configuration_id=request.configuration_id,
        )
    except (ConfigurationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return job_response(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_batch_status(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> JobResponse:
    return job_response(require_job(task_service, job_id))


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_batch(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> JobResponse:
    if not task_service.cancel_job(job_id):
        job = require_job(task_service, job_id)
        return job_response(job)
    return job_response(require_job(task_service, job_id))


@router.get("/{job_id}/result", response_model=JobResultResponse)
def get_batch_result(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> JobResultResponse:
    return completed_result_response(require_job(task_service, job_id))


@router.get("/{job_id}/export/{export_format}")
def export_batch(
    job_id: str,
    export_format: str,
    task_service: TaskService = TaskServiceDependency,
) -> Response:
    if export_format not in EXPORT_FORMATS:
        raise HTTPException(status_code=404, detail="export format not found")
    return export_response(
        require_job(task_service, job_id),
        "batch",
        cast(ExportFormat, export_format),
    )

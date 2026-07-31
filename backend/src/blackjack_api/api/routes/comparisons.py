"""Comparison API routes."""

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Response, status

from blackjack_api.api.routes._jobs import (
    completed_result_response,
    export_response,
    job_response,
    require_job,
)
from blackjack_api.dependencies import get_task_service
from blackjack_api.schemas.analysis import ComparisonStartRequest
from blackjack_api.schemas.jobs import JobResponse, JobResultResponse
from blackjack_api.services import TaskService
from blackjack_api.services.export_service import ExportFormat
from blackjack_simulator.comparison import ComparisonMode
from blackjack_simulator.configuration import ConfigurationError

router = APIRouter(prefix="/comparisons")
TaskServiceDependency = Depends(get_task_service)
EXPORT_FORMATS = {"json", "csv", "zip", "pdf", "chart.svg"}


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def start_comparison(
    request: ComparisonStartRequest,
    task_service: TaskService = TaskServiceDependency,
) -> JobResponse:
    try:
        job = task_service.enqueue_comparison(
            request.configs,
            names=request.names,
            mode=ComparisonMode(request.mode),
            overrides=_overrides(request),
        )
    except (ConfigurationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return job_response(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_comparison_status(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> JobResponse:
    return job_response(require_job(task_service, job_id))


@router.get("/{job_id}/result", response_model=JobResultResponse)
def get_comparison_result(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> JobResultResponse:
    return completed_result_response(require_job(task_service, job_id))


@router.get("/{job_id}/export/{export_format}")
def export_comparison(
    job_id: str,
    export_format: str,
    task_service: TaskService = TaskServiceDependency,
) -> Response:
    if export_format not in EXPORT_FORMATS:
        raise HTTPException(status_code=404, detail="export format not found")
    return export_response(
        require_job(task_service, job_id),
        "comparison",
        cast(ExportFormat, export_format),
    )


def _overrides(request: ComparisonStartRequest) -> dict[str, int]:
    overrides: dict[str, int] = {}
    if request.rounds is not None:
        overrides["rounds"] = request.rounds
    if request.seed is not None:
        overrides["seed"] = request.seed
    if request.workers is not None:
        overrides["workers"] = request.workers
    return overrides

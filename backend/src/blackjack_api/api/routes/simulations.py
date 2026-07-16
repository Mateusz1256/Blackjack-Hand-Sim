"""Simulation API routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from blackjack_api.api.routes._jobs import job_response, require_job
from blackjack_api.dependencies import get_task_service
from blackjack_api.schemas.simulation import (
    SimulationJobResponse,
    SimulationResultResponse,
    SimulationStartRequest,
    SimulationTraceResponse,
    ValidationResponse,
)
from blackjack_api.services import TaskService
from blackjack_api.workers import JobStatus
from blackjack_simulator.configuration import ConfigurationError, parse_app_config

router = APIRouter(prefix="/simulations")
TaskServiceDependency = Depends(get_task_service)


@router.post("/validate", response_model=ValidationResponse)
def validate_simulation(request: SimulationStartRequest) -> ValidationResponse:
    try:
        config = parse_app_config(request.config_text)
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return ValidationResponse(
        valid=True,
        rounds=config.simulation.rounds,
        seed=config.simulation.seed,
        workers=config.simulation.workers,
    )


@router.post(
    "",
    response_model=SimulationJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def start_simulation(
    request: SimulationStartRequest,
    task_service: TaskService = TaskServiceDependency,
) -> SimulationJobResponse:
    try:
        job = task_service.enqueue_simulation(
            request.config_text,
            configuration_id=request.configuration_id,
        )
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return job_response(job)


@router.get("/{job_id}", response_model=SimulationJobResponse)
def get_simulation_status(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> SimulationJobResponse:
    return job_response(require_job(task_service, job_id))


@router.post("/{job_id}/cancel", response_model=SimulationJobResponse)
def cancel_simulation(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> SimulationJobResponse:
    if not task_service.cancel_job(job_id):
        job = require_job(task_service, job_id)
        return job_response(job)
    return job_response(require_job(task_service, job_id))


@router.get("/{job_id}/result", response_model=SimulationResultResponse)
def get_simulation_result(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> SimulationResultResponse:
    job = require_job(task_service, job_id)
    if job.status is JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=job.error or "simulation failed",
        )
    if job.status is JobStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="simulation was cancelled",
        )
    if job.status is not JobStatus.COMPLETED or job.result is None:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="simulation is not complete",
        )
    return SimulationResultResponse(
        job_id=job.id,
        status=job.status.value,
        result=job.result,
    )


@router.get("/{job_id}/trace", response_model=SimulationTraceResponse)
def get_simulation_trace(
    job_id: str,
    task_service: TaskService = TaskServiceDependency,
) -> SimulationTraceResponse:
    job = require_job(task_service, job_id)
    if job.status is not JobStatus.COMPLETED or job.result is None:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="simulation trace is not available yet",
        )
    raw_events = job.result.get("trace_events", [])
    events = raw_events if isinstance(raw_events, list) else []
    return SimulationTraceResponse(job_id=job.id, events=events)

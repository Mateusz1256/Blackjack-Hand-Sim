"""Run history API routes."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from blackjack_api.dependencies import get_run_repository
from blackjack_api.repositories import RunRecord, RunRepository
from blackjack_api.schemas.history import (
    RunHistoryListResponse,
    RunHistoryRecordResponse,
)

router = APIRouter(prefix="/history")
RunRepositoryDependency = Depends(get_run_repository)


@router.get("", response_model=RunHistoryListResponse)
def list_history(
    run_type: str | None = None,
    status_filter: str | None = None,
    limit: int = 50,
    repository: RunRepository = RunRepositoryDependency,
) -> RunHistoryListResponse:
    try:
        runs = repository.list(run_type=run_type, status=status_filter, limit=limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return RunHistoryListResponse(runs=[_run_response(run) for run in runs])


@router.get("/{run_id}", response_model=RunHistoryRecordResponse)
def get_history_run(
    run_id: str,
    repository: RunRepository = RunRepositoryDependency,
) -> RunHistoryRecordResponse:
    run = repository.get(run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="run not found",
        )
    return _run_response(run)


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_run(
    run_id: str,
    repository: RunRepository = RunRepositoryDependency,
) -> Response:
    if not repository.delete(run_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="run not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _run_response(run: RunRecord) -> RunHistoryRecordResponse:
    return RunHistoryRecordResponse(
        id=run.id,
        configuration_id=run.configuration_id,
        run_type=run.run_type,
        status=run.status,
        seed=run.seed,
        rounds=run.rounds,
        config_snapshot=run.config_snapshot,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )

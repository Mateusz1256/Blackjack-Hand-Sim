"""FastAPI dependency helpers."""

from fastapi import Request

from blackjack_api.repositories import PresetRepository, RunRepository
from blackjack_api.services import TaskService


def get_task_service(request: Request) -> TaskService:
    service = request.app.state.task_service
    if not isinstance(service, TaskService):
        msg = "task service is not configured"
        raise RuntimeError(msg)
    return service


def get_preset_repository(request: Request) -> PresetRepository:
    repository = request.app.state.preset_repository
    if not isinstance(repository, PresetRepository):
        msg = "preset repository is not configured"
        raise RuntimeError(msg)
    return repository


def get_run_repository(request: Request) -> RunRepository:
    repository = request.app.state.run_repository
    if not isinstance(repository, RunRepository):
        msg = "run repository is not configured"
        raise RuntimeError(msg)
    return repository

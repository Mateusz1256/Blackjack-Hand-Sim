"""FastAPI dependency helpers."""

from fastapi import Request

from blackjack_api.services import TaskService


def get_task_service(request: Request) -> TaskService:
    service = request.app.state.task_service
    if not isinstance(service, TaskService):
        msg = "task service is not configured"
        raise RuntimeError(msg)
    return service

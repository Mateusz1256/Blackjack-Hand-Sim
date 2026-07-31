"""FastAPI app factory."""

from fastapi import FastAPI

from blackjack_api.api.router import create_api_router
from blackjack_api.config import BackendSettings, get_settings
from blackjack_api.repositories import PresetRepository, RunRepository
from blackjack_api.services import TaskService, open_database
from blackjack_api.workers import LocalTaskQueue
from blackjack_simulator.presets import list_builtin_presets


def create_app(settings: BackendSettings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        summary="HTTP API for Blackjack Simulator analytical workflows.",
        description=(
            "Backend API shell around the public blackjack_simulator engine interfaces."
        ),
    )
    app.state.settings = settings
    connection = open_database(settings.database_path)
    app.state.database_connection = connection
    app.state.run_repository = RunRepository(connection)
    app.state.preset_repository = PresetRepository(connection)
    for preset in list_builtin_presets():
        app.state.preset_repository.upsert(preset)
    app.state.task_service = TaskService(
        queue=LocalTaskQueue(),
        run_repository=app.state.run_repository,
    )
    app.include_router(create_api_router(), prefix=settings.api_prefix)
    return app


app = create_app()

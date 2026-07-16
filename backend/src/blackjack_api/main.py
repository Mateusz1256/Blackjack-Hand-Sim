"""FastAPI app factory."""

from fastapi import FastAPI

from blackjack_api.api.router import create_api_router
from blackjack_api.config import BackendSettings, get_settings


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
    app.include_router(create_api_router(), prefix=settings.api_prefix)
    return app


app = create_app()

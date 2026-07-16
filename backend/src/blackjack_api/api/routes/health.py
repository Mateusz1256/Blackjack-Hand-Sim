"""Health check route."""

from fastapi import APIRouter, Request

import blackjack_simulator
from blackjack_api.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        api_version=settings.version,
        engine_version=blackjack_simulator.__version__,
    )

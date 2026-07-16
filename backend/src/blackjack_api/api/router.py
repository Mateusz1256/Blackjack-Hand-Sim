"""Top-level API router."""

from fastapi import APIRouter

from blackjack_api.api.routes.health import router as health_router
from blackjack_api.api.routes.simulations import router as simulations_router


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health_router, tags=["health"])
    router.include_router(simulations_router, tags=["simulations"])
    return router

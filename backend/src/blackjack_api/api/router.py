"""Top-level API router."""

from fastapi import APIRouter

from blackjack_api.api.routes.batches import router as batches_router
from blackjack_api.api.routes.comparisons import router as comparisons_router
from blackjack_api.api.routes.health import router as health_router
from blackjack_api.api.routes.history import router as history_router
from blackjack_api.api.routes.presets import router as presets_router
from blackjack_api.api.routes.simulations import router as simulations_router


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(batches_router, tags=["batches"])
    router.include_router(comparisons_router, tags=["comparisons"])
    router.include_router(health_router, tags=["health"])
    router.include_router(history_router, tags=["history"])
    router.include_router(presets_router, tags=["presets"])
    router.include_router(simulations_router, tags=["simulations"])
    return router

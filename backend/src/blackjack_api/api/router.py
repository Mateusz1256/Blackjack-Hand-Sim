"""Top-level API router."""

from fastapi import APIRouter

from blackjack_api.api.routes.health import router as health_router


def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health_router, tags=["health"])
    return router

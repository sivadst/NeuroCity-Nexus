from __future__ import annotations

from contextlib import suppress

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import get_settings
from redis.asyncio import Redis
from src.db.session import AsyncSessionLocal
from src.api.v1.endpoints.digital_twin import router as twin_router
from src.api.v1.endpoints.twin_ws import twin_websocket

settings = get_settings()

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(twin_router)


async def health_handler() -> JSONResponse:
    """Return DB and Redis health status for the platform."""
    db_ok = False
    redis_ok = False
    async with AsyncSessionLocal() as session:
        with suppress(Exception):
            await session.execute(text("SELECT 1"))
            db_ok = True
    with suppress(Exception):
        client = Redis.from_url(settings.redis_url, decode_responses=True)
        redis_ok = bool(await client.ping())
        await client.aclose()
    return JSONResponse(
        {
            "status": "healthy" if db_ok and redis_ok else "degraded",
            "database": db_ok,
            "redis": redis_ok,
        }
    )


def register_routes(app: FastAPI) -> None:
    """Register HTTP and websocket routes on the FastAPI application."""
    app.include_router(api_router)
    app.add_api_route("/health", health_handler, methods=["GET"], tags=["Health"])
    app.add_websocket_route("/ws/twin", twin_websocket)

from contextlib import suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.health import check_postgres, check_redis

settings = get_settings()

app = FastAPI(
    title="NeuroCity Nexus API",
    description="Foundational backend services for the NeuroCity Nexus city-brain platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "name": "NeuroCity Nexus API",
        "environment": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health() -> dict[str, object]:
    services = {"database": False, "redis": False}

    with suppress(Exception):
        services["database"] = check_postgres(settings)

    with suppress(Exception):
        services["redis"] = check_redis(settings)

    overall_status = "healthy" if all(services.values()) else "degraded"

    return {
        "status": overall_status,
        "environment": settings.app_env,
        "services": services,
    }

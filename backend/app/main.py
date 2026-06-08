from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from src.api.router import register_routes

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


register_routes(app)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "name": "NeuroCity Nexus API",
        "environment": settings.app_env,
        "docs": "/docs",
    }

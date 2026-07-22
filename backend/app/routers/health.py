"""
routers/health.py — Liveness and readiness check endpoint.

GET /api/health
Returns server status, version, uptime, cache stats, and Firebase readiness.
"""

import time
from fastapi import APIRouter
from app.schemas.common import HealthResponse
from app.cache.memory_cache import cache
from app.services.firebase_service import is_firebase_ready
from config import settings

router = APIRouter()

_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the current status, version, uptime, and cache stats of the backend.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        uptime_seconds=round(time.time() - _start_time, 1),
        environment=settings.app_env,
        cache_stats={
            **cache.stats(),
            "firebase_admin_ready": is_firebase_ready(),
        },
    )

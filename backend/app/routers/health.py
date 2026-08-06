"""
routers/health.py — Liveness and readiness check endpoint.

GET /api/health
Returns server status, version, uptime, cache stats, and Firebase readiness.
"""

import time
import httpx
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.common import HealthResponse, SystemHealthResponse
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


async def _check_api(client: httpx.AsyncClient, name: str, url: str) -> tuple[str, str]:
    try:
        # Any HTTP response (even 4xx/5xx) means the host is reachable and online.
        # Only a network-level exception (timeout, DNS failure, connection refused) means offline.
        await client.get(url, timeout=3.0)
        return name, "online"
    except Exception:
        return name, "offline"

@router.get(
    "/health/system",
    response_model=SystemHealthResponse,
    summary="System health check for Admin Dashboard",
)
async def system_health_check() -> SystemHealthResponse:
    firebase_ready = is_firebase_ready()
    firebase_status = "connected" if firebase_ready else "disconnected"

    apis_to_check = {
        "steam": "https://store.steampowered.com/api/appdetails?appids=10",
        "rawg": "https://api.rawg.io/api/platforms",
        "cheapshark": "https://www.cheapshark.com/api/1.0/deals",
        "itad": "https://api.isthereanydeal.com/games/v1/deals",
        "newsapi": "https://newsapi.org/v2/top-headlines",
        "coingecko": "https://api.coingecko.com/api/v3/ping",
        "frankfurter": "https://api.frankfurter.app/latest",
        "paypal": "https://api-m.sandbox.paypal.com"
    }

    api_results = {}
    
    async with httpx.AsyncClient() as client:
        tasks = [_check_api(client, name, url) for name, url in apis_to_check.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, tuple):
                api_results[res[0]] = res[1]

    fallback = {}
    if api_results.get("rawg") == "offline":
        fallback["rawg"] = "Steam Store API"

    status = "healthy"
    if not firebase_ready:
        status = "warning"
        
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return SystemHealthResponse(
        status=status,
        frontend="online",
        backend="healthy",
        firebase={
            "authentication": firebase_status,
            "firestore": firebase_status
        },
        apis=api_results,
        fallback=fallback,
        lastCheck=now
    )

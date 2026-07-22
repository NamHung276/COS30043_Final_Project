"""
services/free_games_service.py — FreeToGame API calls.

FreeToGame API: https://www.freetogame.com/api-doc
No API key required — public API.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

FREETOGAME_BASE_URL = "https://www.freetogame.com/api"

# ── Cache TTLs ────────────────────────────────────────────────────────────────
TTL_LIST   = 30 * 60  # 30 minutes (free game catalogue changes slowly)
TTL_DETAIL = 30 * 60


async def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """GET request to FreeToGame API."""
    async with httpx.AsyncClient(base_url=FREETOGAME_BASE_URL, timeout=15.0) as client:
        response = await client.get(path, params=params or {})
        response.raise_for_status()
        return response.json()


# ── Public Service Functions ───────────────────────────────────────────────────

async def get_free_games(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[Dict]:
    """
    Fetch all free-to-play games.

    Args:
        platform: "pc" | "browser" | "all"
        category: genre/category string (e.g., "mmorpg", "shooter")
        sort_by: "release-date" | "popularity" | "alphabetical" | "relevance"
        tag:     filter by tag
    """
    cache_key = build_cache_key(
        "freetogame", "list",
        platform or "all", category or "", sort_by or "", tag or "",
    )

    async def _fetch():
        params = {}
        if platform:
            params["platform"] = platform
        if category:
            params["category"] = category
        if sort_by:
            params["sort-by"] = sort_by
        if tag:
            params["tag"] = tag
        return await _get("/games", params)

    return await cache.get_or_set(cache_key, _fetch, ttl=TTL_LIST)


async def get_free_game_detail(game_id: int) -> Dict:
    """Fetch detailed info for a single free-to-play game."""
    cache_key = build_cache_key("freetogame", "detail", game_id)

    return await cache.get_or_set(
        cache_key,
        lambda: _get("/game", {"id": game_id}),
        ttl=TTL_DETAIL,
    )


async def get_free_games_by_category(category: str) -> List[Dict]:
    """Fetch free games filtered to a specific category."""
    return await get_free_games(category=category, sort_by="popularity")

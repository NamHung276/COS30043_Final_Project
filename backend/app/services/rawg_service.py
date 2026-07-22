"""
services/rawg_service.py — All RAWG Video Games Database API calls.

RAWG API docs: https://rawg.io/apidocs
Key features:
  - API key is injected server-side (never sent to the browser)
  - All responses are cached with configurable TTL
  - httpx is used for async HTTP (not requests)
"""

import logging
from typing import Any, Dict, Optional

import httpx

from config import settings
from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

RAWG_BASE_URL = "https://api.rawg.io/api"

# ── Cache TTLs ────────────────────────────────────────────────────────────────
TTL_GAMES_LIST    = 5 * 60   # 5 minutes
TTL_GAME_DETAIL   = 10 * 60  # 10 minutes
TTL_SCREENSHOTS   = 10 * 60
TTL_TRAILERS      = 10 * 60
TTL_SEARCH        = 5 * 60


def _params(**kwargs) -> Dict[str, Any]:
    """Build a params dict that always includes the RAWG API key."""
    p = {"key": settings.rawg_api_key}
    p.update({k: v for k, v in kwargs.items() if v is not None})
    return p


async def _get(path: str, params: Dict[str, Any]) -> Dict:
    """
    Perform a GET request against the RAWG API.
    Raises httpx.HTTPStatusError on non-2xx responses.
    """
    async with httpx.AsyncClient(base_url=RAWG_BASE_URL, timeout=15.0) as client:
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()


# ── Public Service Functions ───────────────────────────────────────────────────

async def get_games(
    page: int = 1,
    page_size: int = 20,
    ordering: str = "-rating",
    genres: Optional[str] = None,
    platforms: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
) -> Dict:
    """
    Fetch a paginated list of games from RAWG.

    Returns:
        RAWG /games response dict with keys: count, next, previous, results
    """
    cache_key = build_cache_key(
        "rawg", "games",
        page, page_size, ordering,
        genres or "", platforms or "",
        search or "", tags or "",
    )

    return await cache.get_or_set(
        cache_key,
        lambda: _get("/games", _params(
            page=page,
            page_size=page_size,
            ordering=ordering,
            genres=genres,
            platforms=platforms,
            search=search,
            tags=tags,
        )),
        ttl=TTL_GAMES_LIST,
    )


async def search_games(query: str, page: int = 1, page_size: int = 20) -> Dict:
    """Search games by name. Results are cached per query+page."""
    cache_key = build_cache_key("rawg", "search", query.lower(), page, page_size)

    return await cache.get_or_set(
        cache_key,
        lambda: _get("/games", _params(
            search=query,
            page=page,
            page_size=page_size,
            search_precise=True,
        )),
        ttl=TTL_SEARCH,
    )


async def get_game_detail(game_id: int) -> Dict:
    """Fetch detailed information for a single game by its RAWG ID."""
    cache_key = build_cache_key("rawg", "game", game_id)

    return await cache.get_or_set(
        cache_key,
        lambda: _get(f"/games/{game_id}", _params()),
        ttl=TTL_GAME_DETAIL,
    )


async def get_screenshots(game_id: int) -> Dict:
    """Fetch all screenshots for a game."""
    cache_key = build_cache_key("rawg", "screenshots", game_id)

    return await cache.get_or_set(
        cache_key,
        lambda: _get(f"/games/{game_id}/screenshots", _params()),
        ttl=TTL_SCREENSHOTS,
    )


async def get_trailers(game_id: int) -> Dict:
    """Fetch trailers/clips for a game (if any)."""
    cache_key = build_cache_key("rawg", "trailers", game_id)

    return await cache.get_or_set(
        cache_key,
        lambda: _get(f"/games/{game_id}/movies", _params()),
        ttl=TTL_TRAILERS,
    )


async def get_similar_games(game_id: int) -> Dict:
    """Fetch games that are similar to the given game."""
    cache_key = build_cache_key("rawg", "similar", game_id)

    return await cache.get_or_set(
        cache_key,
        lambda: _get(f"/games/{game_id}/game-series", _params(page_size=6)),
        ttl=TTL_GAME_DETAIL,
    )

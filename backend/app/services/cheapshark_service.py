"""
services/cheapshark_service.py — CheapShark game deals API calls.

CheapShark API docs: https://apidocs.cheapshark.com/
No API key required — CheapShark is public.
"""

import logging
from typing import Any, Dict, List, Optional, Union

import httpx

from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

CHEAPSHARK_BASE_URL = "https://www.cheapshark.com/api/1.0"

# ── Cache TTLs ────────────────────────────────────────────────────────────────
TTL_DEALS       = 15 * 60   # 15 minutes (deals change often but not by the second)
TTL_STORES      = 60 * 60   # 1 hour (store list is stable)
TTL_GAME_LOOKUP = 10 * 60   # 10 minutes

# Human-readable store names (mirrors what Vue currently hardcodes)
STORE_NAMES: Dict[str, str] = {
    "1":  "Steam",
    "2":  "GamersGate",
    "3":  "GreenManGaming",
    "7":  "GOG",
    "8":  "Origin",
    "11": "Humble Store",
    "13": "Uplay",
    "15": "Fanatical",
    "21": "WinGameStore",
    "23": "GameBillet",
    "24": "Voidu",
    "25": "Epic Games",
    "27": "Games Planet",
    "28": "Games Tradera",
    "29": "Games Republic",
    "30": "Silagrastore",
    "31": "Allyouplay",
    "32": "DLGamer",
    "33": "Noctre",
    "34": "DreamGame",
}


async def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """GET request to CheapShark API."""
    async with httpx.AsyncClient(base_url=CHEAPSHARK_BASE_URL, timeout=15.0) as client:
        response = await client.get(path, params=params or {})
        response.raise_for_status()
        return response.json()


def _enrich_deal(deal: Dict) -> Dict:
    """Add a human-readable store_name field to a deal dict."""
    store_id = str(deal.get("storeID", ""))
    deal["store_name"] = STORE_NAMES.get(store_id, f"Store #{store_id}")
    return deal


# ── Public Service Functions ───────────────────────────────────────────────────

async def get_deals(
    page_number: int = 0,
    page_size: int = 60,
    sort_by: str = "DealRating",
    upper_price: Optional[float] = None,
    lower_price: Optional[float] = None,
    min_savings: Optional[int] = None,
    store_id: Optional[str] = None,
    aaa: Optional[int] = None,
) -> List[Dict]:
    """
    Fetch game deals from CheapShark.

    Returns a list of deal dicts, each enriched with a store_name field.
    """
    cache_key = build_cache_key(
        "cheapshark", "deals",
        page_number, page_size, sort_by,
        upper_price or "", lower_price or "",
        min_savings or "", store_id or "", aaa or "",
    )

    async def _fetch():
        params: Dict[str, Union[str, int, float]] = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortBy": sort_by,
        }
        if upper_price is not None:
            params["upperPrice"] = upper_price
        if lower_price is not None:
            params["lowerPrice"] = lower_price
        if min_savings is not None:
            params["lowerSavings"] = min_savings
        if store_id:
            params["storeID"] = store_id
        if aaa is not None:
            params["AAA"] = aaa

        deals = await _get("/deals", params)
        return [_enrich_deal(d) for d in deals]

    return await cache.get_or_set(cache_key, _fetch, ttl=TTL_DEALS)


async def get_deals_by_game_name(game_name: str, exact: bool = False) -> List[Dict]:
    """
    Look up deals for a specific game by name.
    Used by the aggregated /api/games/{id} endpoint.
    """
    cache_key = build_cache_key("cheapshark", "game", game_name.lower(), exact)

    async def _fetch():
        params = {"title": game_name, "exact": 1 if exact else 0, "limit": 10}
        data = await _get("/games", params)

        # CheapShark /games returns list of {gameID, steamAppID, cheapest, cheapestDealID, ...}
        # For each, we may want to fetch deal details — but to keep it fast, return as-is
        return data if isinstance(data, list) else []

    return await cache.get_or_set(cache_key, _fetch, ttl=TTL_GAME_LOOKUP)


async def get_stores() -> List[Dict]:
    """Fetch the list of supported stores from CheapShark."""
    cache_key = build_cache_key("cheapshark", "stores")

    return await cache.get_or_set(
        cache_key,
        lambda: _get("/stores"),
        ttl=TTL_STORES,
    )

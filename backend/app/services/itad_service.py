"""
services/itad_service.py — IsThereAnyDeal (ITAD) API v2 Integration.

IsThereAnyDeal API docs: https://isthereanydeal.com/dev/api/
Provides official store pricing, historical low price, and store comparison.

Requires ITAD_API_KEY environment variable.
If not provided or lookup fails, returns None gracefully.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from config import settings
from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

ITAD_BASE_URL = "https://api.isthereanydeal.com"

# Cache TTL: 15 minutes (deals update periodically)
TTL_ITAD = 15 * 60


async def get_itad_deals(steam_id: Optional[str] = None, title: Optional[str] = None, country: str = "US") -> Optional[Dict[str, Any]]:
    """
    Fetch pricing and deal information from IsThereAnyDeal.

    Returns a dict with:
      - game_id (str)
      - title (str)
      - current_best (dict: store, price, regular_price, cut, url)
      - historical_low (dict: store, price, cut, date)
      - store_deals (list of deal dicts across official stores)
      - itad_url (str)

    Returns None if:
      - ITAD_API_KEY is missing
      - Game is not found on ITAD
      - API request fails or times out
    """
    api_key = settings.itad_api_key
    if not api_key:
        return None

    if not steam_id and not title:
        return None

    cache_key = build_cache_key("itad", "game_deals", steam_id or "", (title or "").lower().strip(), country)

    async def _fetch() -> Optional[Dict[str, Any]]:
        headers = {
            "User-Agent": "GameHub/3.0 (COS30043 University Project)",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            # ── 1. Lookup Game ID on ITAD ────────────────────────────────────
            itad_game = None
            uuid_cache_key = build_cache_key("itad_uuid", steam_id or "", title or "")
            cached_uuid_info = cache.get(uuid_cache_key)

            if cached_uuid_info:
                itad_game = cached_uuid_info
            else:
                # Try by Steam App ID first
                if steam_id:
                    try:
                        resp = await client.get(
                            f"{ITAD_BASE_URL}/games/lookup/v1",
                            params={"key": api_key, "appid": steam_id},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            itad_game = data.get("game")
                    except Exception as e:
                        logger.debug("ITAD lookup by appid %s failed: %s", steam_id, e)

                # Fallback to title lookup if appid failed or wasn't available
                if not itad_game and title:
                    try:
                        resp = await client.get(
                            f"{ITAD_BASE_URL}/games/lookup/v1",
                            params={"key": api_key, "title": title},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            itad_game = data.get("game")
                    except Exception as e:
                        logger.debug("ITAD lookup by title %s failed: %s", title, e)

                if itad_game and itad_game.get("id"):
                    # Cache the UUID mapping for 7 days to avoid repeated lookups
                    cache.set(uuid_cache_key, itad_game, ttl=604800)

            if not itad_game or not itad_game.get("id"):
                return None

            game_uuid = itad_game["id"]
            game_slug = itad_game.get("slug", "")

            # ── 2. Fetch Overview (Current Best + Historical Low) ──────────────
            overview_data = None
            try:
                resp = await client.post(
                    f"{ITAD_BASE_URL}/games/overview/v2",
                    params={"key": api_key, "country": country},
                    json=[game_uuid],
                )
                if resp.status_code == 200:
                    overview_res = resp.json()
                    prices_list = overview_res.get("prices", [])
                    if prices_list:
                        overview_data = prices_list[0]
            except Exception as e:
                logger.warning("ITAD overview fetch failed for %s: %s", game_uuid, e)

            # ── 3. Fetch Prices across Stores ───────────────────────────────
            store_deals: List[Dict[str, Any]] = []
            try:
                resp = await client.post(
                    f"{ITAD_BASE_URL}/games/prices/v2",
                    params={"key": api_key, "country": country, "nonempty": "true"},
                    json=[game_uuid],
                )
                if resp.status_code == 200:
                    prices_res = resp.json()
                    for item in prices_res:
                        if item.get("id") == game_uuid:
                            for deal in item.get("deals", [])[:10]:
                                shop = deal.get("shop", {})
                                price_info = deal.get("price", {})
                                regular_info = deal.get("regular", {})
                                store_deals.append({
                                    "store_id": shop.get("id"),
                                    "store_name": shop.get("name"),
                                    "price": price_info.get("amount", 0.0),
                                    "regular_price": regular_info.get("amount", 0.0),
                                    "currency": price_info.get("currency", "USD"),
                                    "cut": deal.get("cut", 0),
                                    "url": deal.get("url", ""),
                                })
            except Exception as e:
                logger.warning("ITAD store prices fetch failed for %s: %s", game_uuid, e)

            if not overview_data and not store_deals:
                return None

            # ── Normalize Overview Data ──────────────────────────────────────
            current_best = None
            if overview_data and overview_data.get("current"):
                cur = overview_data["current"]
                shop = cur.get("shop", {})
                price = cur.get("price", {})
                regular = cur.get("regular", {})
                current_best = {
                    "store_name": shop.get("name", "Unknown Store"),
                    "price": price.get("amount", 0.0),
                    "regular_price": regular.get("amount", 0.0),
                    "currency": price.get("currency", "USD"),
                    "cut": cur.get("cut", 0),
                    "url": cur.get("url", ""),
                }

            historical_low = None
            if overview_data and overview_data.get("lowest"):
                low = overview_data["lowest"]
                shop = low.get("shop", {})
                price = low.get("price", {})
                historical_low = {
                    "store_name": shop.get("name", "Unknown Store"),
                    "price": price.get("amount", 0.0),
                    "currency": price.get("currency", "USD"),
                    "cut": low.get("cut", 0),
                    "url": low.get("url", ""),
                    "timestamp": low.get("recorded"),
                }

            return {
                "itad_game_id": game_uuid,
                "title": itad_game.get("title", title),
                "current_best": current_best,
                "historical_low": historical_low,
                "store_deals": store_deals,
                "itad_url": f"https://isthereanydeal.com/game/{game_slug}/info/",
            }

    try:
        return await cache.get_or_set(cache_key, _fetch, ttl=TTL_ITAD)
    except Exception as exc:
        logger.warning("ITAD service exception: %s", exc)
        return None


async def get_itad_trending_deals(limit: int = 30, country: str = "US", sort: str = "trending") -> List[Dict[str, Any]]:
    """
    Fetch trending/top deals from IsThereAnyDeal deals feed.
    """
    api_key = settings.itad_api_key
    if not api_key:
        return []

    cache_key = build_cache_key("itad", "trending_deals", limit, country, sort)

    async def _fetch() -> List[Dict[str, Any]]:
        headers = {
            "User-Agent": "GameHub/3.0 (COS30043 University Project)",
            "Accept": "application/json",
        }
        params = {
            "key": api_key,
            "country": country,
            "limit": min(limit, 50),
        }
        if sort == "cut":
            params["sort"] = "-cut"
        elif sort == "price":
            params["sort"] = "price"
        elif sort == "trending":
            params["sort"] = "-trending"

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                resp = await client.get(f"{ITAD_BASE_URL}/deals/v2", params=params)
                if resp.status_code != 200:
                    logger.warning("ITAD deals endpoint returned status %s", resp.status_code)
                    return []

                data = resp.json()
                items = data.get("list", [])
                results = []

                for item in items:
                    deal = item.get("deal", {})
                    shop = deal.get("shop", {})
                    price = deal.get("price", {})
                    regular = deal.get("regular", {})

                    results.append({
                        "id": item.get("id"),
                        "title": item.get("title", "Game Deal"),
                        "store_id": str(shop.get("id", "")),
                        "store_name": shop.get("name", "Store"),
                        "sale_price": price.get("amount", 0.0),
                        "normal_price": regular.get("amount", 0.0),
                        "currency": price.get("currency", "USD"),
                        "savings": deal.get("cut", 0),
                        "is_historical_low": deal.get("historyLow", False),
                        "url": deal.get("url", ""),
                        "source": "ITAD",
                    })

                return results
        except Exception as exc:
            logger.warning("ITAD trending deals error: %s", exc)
            return []

    try:
        return await cache.get_or_set(cache_key, _fetch, ttl=TTL_ITAD)
    except Exception:
        return []


"""
services/steam_service.py — Steam Store API integration.

Fetches complementary Steam-specific data using the Steam App ID extracted
from RAWG store links. This is ADDITIVE data — RAWG remains the primary
source for all game metadata.

Steam Store API docs: https://store.steampowered.com/api/appdetails
No API key required for public store data.
"""

import logging
import re
from typing import Any, Dict, List, Optional

import httpx

from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

STEAM_API_BASE = "https://store.steampowered.com/api"

# Cache TTL: 24 hours for successful fetches, 5 minutes for rate limit failures
TTL_STEAM_DETAIL_SUCCESS = 24 * 60 * 60
TTL_STEAM_DETAIL_FAIL = 5 * 60


async def get_steam_app_details(steam_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch Steam store details for a game by its Steam App ID.

    Returns a normalized dict with:
        - price_overview  (currency, final_price, discount_percent)
        - supported_languages (list of language names, top 10)
        - categories     (list of category names, e.g. "Single-player")
        - achievements_total (int)
        - steam_url      (str)
        - short_description (str)
        - header_image   (str)

    Returns None if the Steam ID is invalid, the request fails, or Steam
    rate-limits us — the caller should treat None as "section unavailable".
    """
    if not steam_id:
        return None

    cache_key = build_cache_key("steam", "appdetails", steam_id)

    async def _fetch() -> Optional[Dict[str, Any]]:
        params = {
            "appids": steam_id,
            "filters": "price_overview,basic,categories,achievements",
            "cc": "us",
            "l": "english",
        }
        headers = {
            "User-Agent": "GameHub/3.0 (COS30043 University Project)",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                resp = await client.get(f"{STEAM_API_BASE}/appdetails", params=params)

                if resp.status_code == 429:
                    logger.warning("Steam API rate-limited for app %s", steam_id)
                    return None

                resp.raise_for_status()
                data = resp.json()

                app_data = data.get(steam_id, {})
                if not app_data.get("success"):
                    return None

                raw = app_data.get("data", {})
                if not raw:
                    return None

                # ── Normalize price ──────────────────────────────────────────
                price_raw = raw.get("price_overview")
                price = None
                if price_raw:
                    price = {
                        "currency": price_raw.get("currency", "USD"),
                        "initial": price_raw.get("initial", 0) / 100,
                        "final": price_raw.get("final", 0) / 100,
                        "discount_percent": price_raw.get("discount_percent", 0),
                        "initial_formatted": price_raw.get("initial_formatted", ""),
                        "final_formatted": price_raw.get("final_formatted", ""),
                    }

                # ── Normalize languages ──────────────────────────────────────
                lang_str: str = raw.get("supported_languages", "")
                # Steam returns an HTML-ish comma-separated string
                # e.g. "English<strong>*</strong>, French, German"
                clean = re.sub(r"<[^>]+>", "", lang_str)  # strip HTML tags
                langs: List[str] = [
                    lv.strip().replace("*", "").strip()
                    for lv in clean.split(",")
                    if lv.strip()
                ][:10]

                # ── Normalize categories ─────────────────────────────────────
                categories: List[str] = [
                    c.get("description", "")
                    for c in raw.get("categories", [])
                    if c.get("description")
                ][:8]

                # ── Achievements count ───────────────────────────────────────
                achievements_total: int = raw.get("achievements", {}).get("total", 0)

                return {
                    "steam_url": f"https://store.steampowered.com/app/{steam_id}/",
                    "short_description": raw.get("short_description", ""),
                    "header_image": raw.get("header_image", ""),
                    "price": price,
                    "supported_languages": langs,
                    "categories": categories,
                    "achievements_total": achievements_total,
                    "is_free": raw.get("is_free", False),
                }

        except httpx.TimeoutException:
            logger.warning("Steam API timed out for app %s", steam_id)
            return None
        except httpx.HTTPStatusError as exc:
            logger.warning("Steam API HTTP %s for app %s", exc.response.status_code, steam_id)
            return None
        except Exception as exc:
            logger.warning("Steam API error for app %s: %s", steam_id, exc)
            return None

    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        result = await _fetch()
        
        # Determine dynamic TTL: short cooldown for failures/429, 24h for success
        ttl = TTL_STEAM_DETAIL_FAIL if result is None else TTL_STEAM_DETAIL_SUCCESS
        cache.set(cache_key, result, ttl=ttl)
        
        return result
    except Exception as exc:
        logger.warning("Steam cache error for app %s: %s", steam_id, exc)
        return None

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
                    "steam_name": raw.get("name", "Unknown Game"),
                    "steam_url": f"https://store.steampowered.com/app/{steam_id}/",
                    "short_description": raw.get("short_description", ""),
                    "header_image": raw.get("header_image", ""),
                    "price": price,
                    "supported_languages": langs,
                    "categories": categories,
                    "achievements_total": achievements_total,
                    "is_free": raw.get("is_free", False),
                    "release_date": raw.get("release_date", {}).get("date", ""),
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


async def search_games_fallback(query: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Fallback search using Steam Store API when RAWG is down.
    Maps Steam results to look exactly like RAWG GameSummary schema.
    """
    if not query:
        return {"count": 0, "next": None, "previous": None, "results": []}
    
    # Steam storesearch has limited pagination (only works reliably for a few pages)
    # We will just fetch a chunk of items
    params = {
        "term": query,
        "l": "english",
        "cc": "US"
    }
    
    headers = {
        "User-Agent": "GameHub/3.0 (COS30043 University Project)",
        "Accept": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(f"{STEAM_API_BASE}/storesearch/", params=params)
            resp.raise_for_status()
            data = resp.json()
            
            items = data.get("items", [])
            total = data.get("total", 0)
            
            results = []
            for item in items:
                # Map price if it exists
                mapped_price = None
                if "price" in item:
                    mapped_price = {
                        "final": item["price"].get("final", 0) / 100.0,
                        "initial": item["price"].get("initial", 0) / 100.0,
                        "discount_percent": 0  # storesearch does not seem to return discount_percent directly, but we can compute it or leave it 0
                    }
                    if mapped_price["initial"] > 0 and mapped_price["final"] < mapped_price["initial"]:
                        mapped_price["discount_percent"] = round((1 - mapped_price["final"] / mapped_price["initial"]) * 100)

                # Format to match GameSummary
                results.append({
                    "id": f"steam-{item['id']}",  # Prefix so frontend/backend knows it's a steam ID
                    "name": item.get("name", "Unknown Game"),
                    "slug": str(item.get("id", "")),
                    "background_image": item.get("tiny_image", ""),
                    "released": None,
                    "metacritic": int(item.get("metascore")) if item.get("metascore") else None,
                    "rating": None,
                    "ratings_count": None,
                    "genres": [],
                    "platforms": [],
                    "tags": [],
                    "short_screenshots": [],
                    "price": mapped_price
                })
                
            return {
                "count": total,
                "next": None,  # Steam API doesn't do cursor pagination nicely here
                "previous": None,
                "results": results
            }
            
    except Exception as exc:
        logger.warning("Steam search fallback failed for query %s: %s", query, exc)
        # If Steam fails too, return empty 
        return {"count": 0, "next": None, "previous": None, "results": []}


async def get_game_detail_fallback(steam_id: str) -> Dict[str, Any]:
    """
    Fallback detail fetcher when RAWG is down. Uses the existing get_steam_app_details
    and wraps it in a UnifiedGameDetail-compatible dictionary.
    """
    # Remove the "steam-" prefix if it exists
    clean_id = steam_id.replace("steam-", "")
    
    steam_data = await get_steam_app_details(clean_id)
    if not steam_data:
        raise Exception(f"Steam API returned no data for app {clean_id}")
        
    # Map to UnifiedGameDetail structure
    
    # Format the price for UnifiedPrice
    mapped_price = None
    steam_price = steam_data.get("price")
    if steam_price:
        mapped_price = {
            "currency": steam_price.get("currency", "USD"),
            "initial": steam_price.get("initial", 0.0),
            "final": steam_price.get("final", 0.0),
            "discount_percent": steam_price.get("discount_percent", 0),
            "store_name": "Steam",
            "url": steam_data.get("steam_url", ""),
            "source": "Steam API Fallback"
        }
        
    return {
        "id": f"steam-{clean_id}",
        "title": steam_data.get("steam_name", "Game Details from Steam"),
        "slug": clean_id,
        "description": steam_data.get("short_description", "Description unavailable."),
        "hero_image": steam_data.get("header_image", ""),
        "cover_image": steam_data.get("header_image", ""),
        "released": steam_data.get("release_date", "2023-01-01") or "2023-01-01",
        "metacritic": None,
        "website": steam_data.get("steam_url", ""),
        
        # Meta
        "screenshots": [steam_data.get("header_image", "")],
        
        # Collections
        "genres": [c for c in steam_data.get("categories", [])],
        "developers": [],
        "publishers": [],
        "platforms": ["PC"],
        
        # Enrichment from Steam
        "languages": steam_data.get("supported_languages", []),
        "categories": steam_data.get("categories", []),
        "achievements_total": steam_data.get("achievements_total", 0),
        
        # Fallback-Prioritized Blocks
        "price": mapped_price,
        "historical_low": None,
        "players": None,
        "trailer": None,
        
        # Extra data arrays
        "store_deals": [],
        "bundles": [],
        
        # Metadata
        "rawg_url": "",
        "steam_url": steam_data.get("steam_url", ""),
        "aggregated_at": "Just now",
        
        # Sub-schemas for legacy components
        "rawg_screenshots": [],
        "rawg_trailers": [],
        "deals": [], # Can't fetch deals easily without title
        
        # Extended fields from Steam/Steamcharts
        "steam_data": steam_data,
        "steamcharts_data": None
    }


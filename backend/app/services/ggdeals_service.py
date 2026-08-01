import os
import httpx
import logging
from typing import Dict, Any, Optional

from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key
from config import settings

logger = logging.getLogger(__name__)

GGDEALS_BASE_URL = "https://api.gg.deals/v1/prices/by-steam-app-id/"
GGDEALS_BUNDLES_URL = "https://api.gg.deals/v1/bundles/by-steam-app-id/"
GGDEALS_ACTIVE_BUNDLES_URL = "https://api.gg.deals/v1/bundles/active/"

async def get_prices_by_steam_id(steam_id: str, region: str = "us") -> Optional[Dict[str, Any]]:
    """
    Fetch exact retail and keyshop pricing data for a game using its Steam App ID.
    Returns the GamePrices object for the given ID, or None.
    """
    api_key = settings.gg_deals_api_key
    if not api_key:
        logger.warning("GG_DEALS_API_KEY is not set. Skipping GG.deals lookup.")
        return None

    cache_key = build_cache_key("ggdeals", "steam_id", steam_id, region)
    async def _fetch():
        params = {
            "key": api_key,
            "ids": steam_id,
            "region": region
        }
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(GGDEALS_BASE_URL, params=params)
            if resp.status_code == 429:
                logger.warning("GG.deals rate limit exceeded.")
                return None
            resp.raise_for_status()
            data = resp.json()
            if data.get("success") and "data" in data:
                return data["data"].get(steam_id)
        return None

    try:
        return await cache.get_or_set(cache_key, _fetch, ttl=900)
    except Exception as exc:
        logger.warning(f"Error fetching GG.deals for steam_id {steam_id}: {exc}")
        
    return None

async def get_bundles_by_steam_id(steam_id: str, region: str = "us") -> Optional[Dict[str, Any]]:
    """
    Fetch bundle data for a game using its Steam App ID.
    Returns the GameBundles object for the given ID, or None.
    """
    api_key = os.getenv("GG_DEALS_API_KEY")
    if not api_key:
        return None

    cache_key = build_cache_key("ggdeals_bundles", "steam_id", steam_id, region)
    async def _fetch():
        params = {
            "key": api_key,
            "ids": steam_id,
            "region": region
        }
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(GGDEALS_BUNDLES_URL, params=params)
            if resp.status_code == 429:
                logger.warning("GG.deals bundles rate limit exceeded.")
                return None
            resp.raise_for_status()
            data = resp.json()
            if data.get("success") and "data" in data:
                return data["data"].get(steam_id)
        return None

    try:
        return await cache.get_or_set(cache_key, _fetch, ttl=900)
    except Exception as exc:
        logger.warning(f"Error fetching GG.deals bundles for steam_id {steam_id}: {exc}")
        
    return None

async def get_active_bundles(region: str = "us", cursor: Optional[str] = None, offset: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch all currently active bundles.
    """
    api_key = os.getenv("GG_DEALS_API_KEY")
    if not api_key:
        return None

    cache_key = build_cache_key("ggdeals_active_bundles", region, cursor or "none", offset or 0)
    async def _fetch():
        params = {
            "key": api_key,
            "region": region
        }
        if cursor:
            params["cursor"] = cursor
        if offset is not None:
            params["offset"] = str(offset)
            
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(GGDEALS_ACTIVE_BUNDLES_URL, params=params)
            if resp.status_code == 429:
                logger.warning("GG.deals active bundles rate limit exceeded.")
                return None
            resp.raise_for_status()
            data = resp.json()
            if data.get("success") and "data" in data:
                return data["data"]
        return None

    try:
        return await cache.get_or_set(cache_key, _fetch, ttl=1800)
    except Exception as exc:
        logger.warning(f"Error fetching GG.deals active bundles: {exc}")
        
    return None


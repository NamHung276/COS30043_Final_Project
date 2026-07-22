"""
coingecko_service.py — CoinGecko API Integration with caching
"""

import logging
import httpx
import time
from typing import Dict, Any, Tuple
from config import settings

logger = logging.getLogger(__name__)

class CoinGeckoService:
    def __init__(self):
        self.api_key = settings.coingecko_api_key
        # Free API base URL
        self.base_url = "https://api.coingecko.com/api/v3"
        # Cache dictionary: { key: (timestamp, data) }
        self.cache: Dict[str, Tuple[float, Any]] = {}
        self.cache_ttl = 300  # 5 minutes in seconds

    async def _fetch_with_cache(self, url: str, params: dict | None = None) -> Any:
        # Create a cache key from url and params
        cache_key = f"{url}?{'-'.join([f'{k}={v}' for k,v in (params or {}).items()])}"
        
        # Check cache
        current_time = time.time()
        if cache_key in self.cache:
            timestamp, data = self.cache[cache_key]
            if current_time - timestamp < self.cache_ttl:
                return data
                
        headers = {}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{url}",
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Save to cache
                self.cache[cache_key] = (current_time, data)
                return data
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch from CoinGecko {url}: {e}")
                # Fallback to expired cache if available, otherwise raise
                if cache_key in self.cache:
                    logger.warning("Returning stale cache due to fetch error.")
                    return self.cache[cache_key][1]
                raise Exception("Failed to fetch data from CoinGecko API") from e

    async def get_trending(self) -> dict:
        """
        Fetch trending search coins on CoinGecko.
        """
        return await self._fetch_with_cache("/search/trending")

    async def get_gaming_coins(self) -> list:
        """
        Fetch top gaming category coins with detailed market data.
        """
        params = {
            "vs_currency": "usd",
            "category": "gaming",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": "false"
        }
        return await self._fetch_with_cache("/coins/markets", params=params)

coingecko_service = CoinGeckoService()

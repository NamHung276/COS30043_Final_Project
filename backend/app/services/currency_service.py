import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.cache.memory_cache import cache
from app.utils.helpers import build_cache_key

logger = logging.getLogger(__name__)

FRANKFURTER_BASE_URL = "https://api.frankfurter.dev/v1"

async def get_currencies() -> Optional[Dict[str, str]]:
    """
    Fetch all supported currencies and their full names.
    e.g. {"USD": "United States Dollar", "EUR": "Euro", ...}
    """
    cache_key = build_cache_key("frankfurter", "currencies")
    
    async def _fetch():
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(f"{FRANKFURTER_BASE_URL}/currencies")
            resp.raise_for_status()
            return resp.json()

    try:
        # Cache for 24 hours since currencies rarely change
        return await cache.get_or_set(cache_key, _fetch, ttl=86400)
    except Exception as exc:
        logger.warning(f"Error fetching Frankfurter currencies: {exc}")
        return None

async def convert_currency(from_curr: str, to_curr: str, amount: float = 1.0) -> Optional[Dict[str, Any]]:
    """
    Convert an amount from one currency to another using latest rates.
    """
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()
    
    if from_curr == to_curr:
        return {
            "amount": amount,
            "base": from_curr,
            "rates": {to_curr: amount},
            "converted_amount": amount
        }

    # We cache rates per currency pair for 1 hour to prevent spam
    cache_key = build_cache_key("frankfurter", "convert", from_curr, to_curr)
    
    async def _fetch():
        params = {
            "from": from_curr,
            "to": to_curr
        }
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(f"{FRANKFURTER_BASE_URL}/latest", params=params)
            resp.raise_for_status()
            return resp.json()

    try:
        data = await cache.get_or_set(cache_key, _fetch, ttl=3600)
        if data and "rates" in data and to_curr in data["rates"]:
            rate = data["rates"][to_curr]
            converted = amount * rate
            return {
                "amount": amount,
                "base": from_curr,
                "rates": {to_curr: rate},
                "converted_amount": round(converted, 2)
            }
        return None
    except Exception as exc:
        logger.warning(f"Error converting {from_curr} to {to_curr}: {exc}")
        return None

async def get_currency_history(from_curr: str, to_curr: str, days: int = 30) -> Optional[Dict[str, Any]]:
    """
    Fetch historical exchange rates for a currency pair.
    """
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()
    
    if from_curr == to_curr:
        return None
        
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    cache_key = build_cache_key("frankfurter", "history", from_curr, to_curr, start_str, end_str)
    
    async def _fetch():
        params = {
            "from": from_curr,
            "to": to_curr
        }
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(f"{FRANKFURTER_BASE_URL}/{start_str}..{end_str}", params=params)
            resp.raise_for_status()
            return resp.json()

    try:
        # Cache for 12 hours since historical data for past dates doesn't change often
        return await cache.get_or_set(cache_key, _fetch, ttl=43200)
    except Exception as exc:
        logger.warning(f"Error fetching history {from_curr} to {to_curr}: {exc}")
        return None

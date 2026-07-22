"""
crypto_service.py — CoinGecko API Integration
"""

import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self):
        self.api_key = settings.coingecko_api_key
        # Free API base URL
        self.base_url = "https://api.coingecko.com/api/v3"

    async def get_exchange_rates(self, vs_currency: str = "usd", ids: str = "bitcoin,ethereum,tether") -> dict:
        """
        Fetch exchange rates for specified cryptocurrencies.
        `ids` should be comma-separated CoinGecko coin IDs.
        """
        headers = {}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key

        params = {
            "ids": ids,
            "vs_currencies": vs_currency
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/simple/price",
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch CoinGecko rates: {e}")
                raise Exception("Failed to fetch crypto exchange rates") from e

crypto_service = CryptoService()

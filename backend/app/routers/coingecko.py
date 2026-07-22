"""
coingecko.py — CoinGecko API routes for gaming cryptocurrencies
"""

import logging
from fastapi import APIRouter, HTTPException, status
from app.services.coingecko_service import coingecko_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/trending")
async def get_trending_crypto():
    """
    Returns trending cryptocurrencies across the entire market on CoinGecko.
    """
    try:
        data = await coingecko_service.get_trending()
        # Extract coins array
        return {"coins": data.get("coins", [])}
    except Exception as e:
        logger.error(f"Error fetching trending crypto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trending crypto"
        )

@router.get("/gaming")
async def get_gaming_coins():
    """
    Returns top gaming coins summary (ID, Name, Symbol).
    """
    try:
        data = await coingecko_service.get_gaming_coins()
        # Just return a summary list as requested
        summary = [{"id": coin.get("id"), "name": coin.get("name"), "symbol": coin.get("symbol")} for coin in data]
        return {"coins": summary}
    except Exception as e:
        logger.error(f"Error fetching gaming crypto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch gaming crypto"
        )

@router.get("/market")
async def get_gaming_market():
    """
    Returns detailed market data for top gaming coins (Price, 24h Change, Market Cap, Volume, Rank).
    """
    try:
        data = await coingecko_service.get_gaming_coins()
        return {"coins": data}
    except Exception as e:
        logger.error(f"Error fetching gaming crypto market data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch gaming crypto market data"
        )

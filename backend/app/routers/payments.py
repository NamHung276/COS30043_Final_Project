"""
payments.py — Payment API routes (PayPal & CoinGecko)
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.payments import (
    OrderCreateRequest,
    OrderCaptureRequest,
    OrderResponse,
    CryptoRatesResponse,
)
from app.services.payment_service import payment_service
from app.services.crypto_service import crypto_service
from app.utils.dependencies import get_current_user
from app.models.user import UserContext
from app.services import rawg_service, cheapshark_service, steam_service
from fastapi import Depends
import logging
import re

logger = logging.getLogger(__name__)

router = APIRouter()





@router.get("/crypto-rates", response_model=CryptoRatesResponse)
async def get_crypto_rates(currency: str = "usd"):
    """
    Returns the current exchange rates for popular cryptocurrencies (BTC, ETH, USDT) against the given fiat currency.
    Used to display crypto equivalent prices at checkout.
    """
    try:
        rates = await crypto_service.get_exchange_rates(vs_currency=currency)
        return CryptoRatesResponse(rates=rates)
    except Exception as e:
        logger.error(f"Error fetching crypto rates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch crypto rates",
        )

"""
payments.py — Payment API routes (PayPal & CoinGecko)
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.payments import OrderCreateRequest, OrderCaptureRequest, OrderResponse, CryptoRatesResponse
from app.services.payment_service import payment_service
from app.services.crypto_service import crypto_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/paypal/create-order", response_model=OrderResponse)
async def create_paypal_order(request: OrderCreateRequest):
    """
    Creates a new PayPal order with the specified amount.
    Returns the order ID which the frontend uses to render the PayPal button.
    """
    try:
        order_data = await payment_service.create_order(
            amount=request.amount,
            currency=request.currency,
            description=request.description
        )
        return OrderResponse(
            order_id=order_data.get("id", ""),
            status=order_data.get("status", "CREATED")
        )
    except Exception as e:
        logger.error(f"Error creating PayPal order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create PayPal order"
        )

@router.post("/paypal/capture-order", response_model=dict)
async def capture_paypal_order(request: OrderCaptureRequest):
    """
    Captures the funds for an approved PayPal order.
    The frontend calls this after the user approves the payment in the PayPal popup.
    """
    try:
        capture_data = await payment_service.capture_order(order_id=request.order_id)
        return capture_data
    except Exception as e:
        logger.error(f"Error capturing PayPal order {request.order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture PayPal order"
        )

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
            detail="Failed to fetch crypto rates"
        )

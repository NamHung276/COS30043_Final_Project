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
from app.services import rawg_service, cheapshark_service
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/paypal/create-order", response_model=OrderResponse)
async def create_paypal_order(
    request: OrderCreateRequest,
    user: UserContext = Depends(get_current_user)
):
    """
    Creates a new PayPal order by calculating the total amount from game IDs.
    Returns the order ID which the frontend uses to render the PayPal button.
    """
    try:
        # Secure Price Calculation
        total_amount = 0.0
        for game_id in request.items:
            try:
                game = await rawg_service.get_game_detail(game_id)
                import re
                steam_id = None
                stores = game.get("stores", [])
                for s in stores:
                    store_info = s.get("store", {})
                    if store_info.get("slug") == "steam" or store_info.get("id") == 1:
                        url = s.get("url", "")
                        if "/app/" in url:
                            match = re.search(r'/app/(\d+)', url)
                            if match:
                                steam_id = match.group(1)
                                break
                
                # First check CheapShark
                cs_results = await cheapshark_service.get_deals_by_game_name(game.get("name", ""))
                cheapest_price = None
                if cs_results:
                    valid_results = []
                    if steam_id:
                        valid_results = [g for g in cs_results if g.get("steamAppID") == steam_id]
                    if not valid_results:
                        valid_results = [g for g in cs_results if g.get("external", "").lower() == game.get("name", "").lower()]
                        
                    best = min(valid_results, key=lambda g: float(g.get("cheapest", "9999")), default=None)
                    if best:
                        cheapest_price = best.get("cheapest")
                
                if cheapest_price:
                    final_price = float(cheapest_price)
                else:
                    # Tier logic
                    year_str = game.get("released")
                    year = int(year_str.split("-")[0]) if year_str else 2020
                    score = game.get("metacritic") or (game.get("rating", 0) * 20) or 70
                    
                    if year >= 2023 and score >= 80:
                        final_price = 59.99
                    elif year >= 2022 or score >= 85:
                        final_price = 49.99
                    elif year >= 2018 or score >= 75:
                        final_price = 29.99
                    elif year >= 2015:
                        final_price = 19.99
                    else:
                        final_price = 9.99
                        
                # Apply old pseudo-discount logic if needed, or just use the tier price.
                # Actually, the frontend cart price logic also applies discounts. 
                # Let's match frontend exact logic! Frontend discount logic was in displayDiscount.
                roll = game_id % 4
                is_sale = roll in (0, 1)
                discount = 40 if roll == 0 else (25 if roll == 1 else 0)
                final_price = final_price * (1 - discount / 100) if is_sale else final_price
                
                total_amount += final_price
            except Exception as ex:
                logger.error(f"Error fetching price for game {game_id}: {ex}")
                # Safe fallback
                total_amount += 19.99

        # Round to 2 decimal places to match PayPal requirements
        final_total = round(total_amount, 2)
        if final_total <= 0:
            raise ValueError("Cart total must be greater than 0")

        order_data = await payment_service.create_order(
            amount=final_total,
            currency=request.currency,
            description=request.description,
        )
        return OrderResponse(
            order_id=order_data.get("id", ""),
            status=order_data.get("status", "CREATED"),
        )
    except Exception as e:
        logger.error(f"Error creating PayPal order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create PayPal order",
        )


@router.post("/paypal/capture-order", response_model=dict)
async def capture_paypal_order(
    request: OrderCaptureRequest,
    user: UserContext = Depends(get_current_user)
):
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
            detail="Failed to capture PayPal order",
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
            detail="Failed to fetch crypto rates",
        )

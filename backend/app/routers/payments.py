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


from app.routers.games import get_game_detail

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
        # Use the pre-calculated amount from the frontend (which already ran through
        # the full ITAD + CheapShark + Steam pipeline on the game detail page).
        # This guarantees PayPal charges exactly what the cart displays.
        if request.amount and request.amount > 0:
            final_total = round(request.amount, 2)
        else:
            # Fallback: recalculate from game IDs (used when amount is not provided)
            total_amount = 0.0
            for game_id in request.items:
                try:
                    game_id_str = str(game_id)
                    game_data = await get_game_detail(game_id_str)
                    price_info = game_data.get("price")
                    if price_info and price_info.get("final") is not None:
                        total_amount += float(price_info["final"])
                    else:
                        logger.error(f"No live price available for game {game_id}")
                        raise ValueError(f"Game {game_data.get('title', game_id)} is currently unavailable for purchase (no price found).")
                except ValueError as ve:
                    raise ve
                except Exception as ex:
                    logger.error(f"Error fetching price for game {game_id}: {ex}")
                    raise ValueError(f"Game {game_id} is currently unavailable for purchase (error).")
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
        
        payment_status = capture_data.get("status")
        if payment_status != "COMPLETED":
            return {"success": False, "error": f"Payment status: {payment_status}"}
            
        payer_name = "Anonymous"
        if "payer" in capture_data and "name" in capture_data["payer"]:
            name_obj = capture_data["payer"]["name"]
            payer_name = f"{name_obj.get('given_name', '')} {name_obj.get('surname', '')}".strip()
            
        transaction_id = capture_data.get("id")
        amount = 0.0
        
        # Try to extract the captured amount from purchase_units
        if "purchase_units" in capture_data and len(capture_data["purchase_units"]) > 0:
            payments = capture_data["purchase_units"][0].get("payments", {})
            captures = payments.get("captures", [])
            if captures:
                transaction_id = captures[0].get("id", transaction_id)
                amount = float(captures[0].get("amount", {}).get("value", 0))
                
        return {
            "success": True,
            "transaction_id": transaction_id,
            "payer": payer_name,
            "amount": amount
        }
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

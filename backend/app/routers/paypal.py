"""
paypal.py — PayPal API routes for checkout
Supports both single-game and cart (multi-item) checkout.
"""

import logging
import re
from typing import List, Optional, Union
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.services.paypal_service import paypal_service
from app.services import rawg_service, cheapshark_service, steam_service
from app.utils.dependencies import get_current_user
from app.models.user import UserContext

logger = logging.getLogger(__name__)

router = APIRouter()


from app.routers.games import get_game_detail

class CreateOrderRequest(BaseModel):
    # Cart-style (multi-game): pass items array
    items: Optional[List[Union[int, str]]] = None
    title: Optional[str] = "GameHub Purchase"
    amount: Optional[float] = None
    # Legacy single-game fields kept for backwards-compat
    gameId: Optional[str] = None
    price: Optional[float] = None


class CaptureOrderRequest(BaseModel):
    orderId: Optional[str] = None
    order_id: Optional[str] = None


@router.post("/create-order")
async def create_paypal_order(request: CreateOrderRequest):
    """
    Creates a new PayPal order.
    Supports:
      - Cart mode: { items: ["steam-730", "297588"], title: "GameHub Checkout", amount: 15.99 }
      - Legacy mode: { gameId: "steam-730", title: "Naval Action", price: 49.99 }
    """
    try:
        if request.items:
            # ── Cart / multi-item mode ──────────────────────────────────────
            # Use the pre-calculated amount from the frontend to ensure exact price match.
            if request.amount and request.amount > 0:
                total = round(request.amount, 2)
            else:
                total = 0.0
                for gid in request.items:
                    game_id_str = str(gid)
                    game_data = await get_game_detail(game_id_str)
                    price_info = game_data.get("price")
                    if price_info and price_info.get("final") is not None:
                        total += float(price_info["final"])
                    else:
                        raise ValueError(f"Game {game_id_str} is currently unavailable for purchase (no price found).")
            
            total = max(round(total, 2), 0.01)

            # Use first item ID as the "game_id" for PayPal reference
            ref_id = str(request.items[0]) if request.items else "cart"
            order_id = await paypal_service.create_order(
                game_id=ref_id,
                title=request.title or "GameHub Checkout",
                price=total,
            )

        elif request.gameId and request.price is not None:
            # ── Legacy single-game mode ────────────────────────────────────
            order_id = await paypal_service.create_order(
                game_id=request.gameId,
                title=request.title or "GameHub Purchase",
                price=request.price,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provide either 'items' (cart) or 'gameId' + 'price' (single game).",
            )

        if not order_id:
            raise ValueError("No order ID returned from PayPal.")

        return {"orderId": order_id, "order_id": order_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating PayPal order: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create PayPal order",
        )


@router.post("/capture-order")
async def capture_paypal_order(request: CaptureOrderRequest):
    """
    Captures the funds for an approved PayPal order.
    """
    try:
        oid = request.orderId or request.order_id
        if not oid:
            raise ValueError("No order ID provided for capture")
        capture_data = await paypal_service.capture_order(order_id=oid)
        return capture_data
    except Exception as e:
        logger.error("Error capturing PayPal order %s: %s", request.orderId or request.order_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture PayPal order",
        )

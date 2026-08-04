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


class CreateOrderRequest(BaseModel):
    # Cart-style (multi-game): pass items array
    items: Optional[List[Union[int, str]]] = None
    title: Optional[str] = "GameHub Purchase"
    # Legacy single-game fields kept for backwards-compat
    gameId: Optional[str] = None
    price: Optional[float] = None


class CaptureOrderRequest(BaseModel):
    orderId: Optional[str] = None
    order_id: Optional[str] = None


async def _calculate_price(game_id: Union[int, str]) -> float:
    """Calculate the server-side price for a single game ID."""
    game_id_str = str(game_id)
    try:
        if game_id_str.startswith("steam-"):
            game = await steam_service.get_game_detail_fallback(game_id_str)
            steam_price = game.get("price")
            if steam_price and steam_price.get("final", 0) > 0:
                return float(steam_price["final"])
            return 17.99  # Safe Steam fallback

        # RAWG integer ID
        game_id_int = int(game_id)
        game = await rawg_service.get_game_detail(game_id_int)

        # Check CheapShark first
        steam_id = None
        for s in game.get("stores", []):
            store_info = s.get("store", {})
            if store_info.get("slug") == "steam" or store_info.get("id") == 1:
                url = s.get("url", "")
                m = re.search(r'/app/(\d+)', url)
                if m:
                    steam_id = m.group(1)
                    break

        cs_results = await cheapshark_service.get_deals_by_game_name(game.get("name", ""))
        if cs_results:
            valid = [g for g in cs_results if g.get("steamAppID") == steam_id] if steam_id else []
            if not valid:
                valid = [g for g in cs_results if g.get("external", "").lower() == game.get("name", "").lower()]
            best = min(valid, key=lambda g: float(g.get("cheapest", "9999")), default=None)
            if best:
                return float(best["cheapest"])

        # Try CheapShark
        cheapest_deal = game.get("cheapest_deal_price")
        if cheapest_deal:
            return float(cheapest_deal)
            
        # No live price available
        logger.error(f"No live price available for game {game_id}")
        raise ValueError(f"Game {game.get('name', game_id)} is currently unavailable for purchase (no price found).")

    except ValueError as ve:
        raise ve
    except Exception as exc:
        logger.error(f"Price calc failed for {game_id}: {exc}")
        raise ValueError(f"Game {game_id} is currently unavailable for purchase (error).")


@router.post("/create-order")
async def create_paypal_order(request: CreateOrderRequest):
    """
    Creates a new PayPal order.
    Supports:
      - Cart mode: { items: ["steam-730", "297588"], title: "GameHub Checkout" }
      - Legacy mode: { gameId: "steam-730", title: "Naval Action", price: 49.99 }
    """
    try:
        if request.items:
            # ── Cart / multi-item mode ──────────────────────────────────────
            total = 0.0
            for gid in request.items:
                total += await _calculate_price(gid)
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

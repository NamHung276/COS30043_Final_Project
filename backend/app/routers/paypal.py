"""
paypal.py — PayPal API routes for checkout
"""

import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.paypal_service import paypal_service

logger = logging.getLogger(__name__)

router = APIRouter()

class CreateOrderRequest(BaseModel):
    gameId: str
    title: str
    price: float

class CaptureOrderRequest(BaseModel):
    orderId: str

@router.post("/create-order")
async def create_paypal_order(request: CreateOrderRequest):
    """
    Creates a new PayPal order with the given game info.
    Returns the order ID for the frontend to render the PayPal button.
    """
    try:
        order_id = await paypal_service.create_order(
            game_id=request.gameId,
            title=request.title,
            price=request.price
        )
        if not order_id:
            raise ValueError("Failed to obtain order ID from PayPal.")
        return {"orderId": order_id}
    except Exception as e:
        logger.error(f"Error creating PayPal order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create PayPal order"
        )

@router.post("/capture-order")
async def capture_paypal_order(request: CaptureOrderRequest):
    """
    Captures the funds for an approved PayPal order.
    """
    try:
        capture_data = await paypal_service.capture_order(order_id=request.orderId)
        return capture_data
    except Exception as e:
        logger.error(f"Error capturing PayPal order {request.orderId}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture PayPal order"
        )

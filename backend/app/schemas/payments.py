"""
payments.py — Pydantic schemas for the payment API
"""

from pydantic import BaseModel, Field


from typing import List

class OrderCreateRequest(BaseModel):
    items: List[int] = Field(..., description="List of game IDs to purchase")
    currency: str = Field(default="USD", description="Currency code (e.g., USD, EUR)")
    description: str = Field(
        default="GameHub Purchase", description="Description of the purchase"
    )


class OrderCaptureRequest(BaseModel):
    order_id: str = Field(..., description="The PayPal Order ID to capture")


class OrderResponse(BaseModel):
    order_id: str = Field(..., description="The created PayPal Order ID")
    status: str = Field(..., description="Order status")


class CryptoRatesResponse(BaseModel):
    rates: dict = Field(..., description="Exchange rates from CoinGecko")

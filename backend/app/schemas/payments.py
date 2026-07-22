"""
payments.py — Pydantic schemas for the payment API
"""

from pydantic import BaseModel, Field

class OrderCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="The amount to charge the user")
    currency: str = Field(default="USD", description="Currency code (e.g., USD, EUR)")
    description: str = Field(default="GameHub Purchase", description="Description of the purchase")

class OrderCaptureRequest(BaseModel):
    order_id: str = Field(..., description="The PayPal Order ID to capture")

class OrderResponse(BaseModel):
    order_id: str = Field(..., description="The created PayPal Order ID")
    status: str = Field(..., description="Order status")

class CryptoRatesResponse(BaseModel):
    rates: dict = Field(..., description="Exchange rates from CoinGecko")

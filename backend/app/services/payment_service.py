"""
payment_service.py — PayPal API Integration
"""

import logging
import base64
import httpx
from config import settings

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.client_id = settings.paypal_client_id
        self.client_secret = settings.paypal_client_secret
        self.mode = settings.paypal_mode
        self.base_url = (
            "https://api-m.sandbox.paypal.com"
            if self.mode == "sandbox"
            else "https://api-m.paypal.com"
        )
        # In a real production app, cache this token until it expires
        self._access_token = None

    async def _get_access_token(self) -> str:
        """Fetch a new access token from PayPal using client credentials."""
        if not self.client_id or not self.client_secret:
            raise ValueError("PayPal credentials are not configured.")

        auth_string = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/oauth2/token",
                    headers=headers,
                    data=data,
                    timeout=10.0
                )
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                return self._access_token
            except httpx.HTTPError as e:
                logger.error(f"Failed to authenticate with PayPal: {e}")
                raise Exception("PayPal authentication failed") from e

    async def create_order(self, amount: float, currency: str = "USD", description: str = "GameHub Purchase") -> dict:
        """Create a new PayPal order."""
        token = await self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "description": description,
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}",
                    },
                }
            ],
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v2/checkout/orders",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to create PayPal order: {e}")
                raise Exception("Failed to create PayPal order") from e

    async def capture_order(self, order_id: str) -> dict:
        """Capture a previously approved PayPal order."""
        token = await self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to capture PayPal order: {e}")
                raise Exception("Failed to capture PayPal order") from e

payment_service = PaymentService()

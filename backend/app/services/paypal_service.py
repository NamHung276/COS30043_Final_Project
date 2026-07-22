"""
paypal_service.py — PayPal Sandbox Integration
"""

import logging
import base64
import httpx
from config import settings

logger = logging.getLogger(__name__)

class PayPalService:
    def __init__(self):
        self.client_id = settings.paypal_client_id
        self.client_secret = settings.paypal_client_secret
        self.mode = settings.paypal_mode
        self.base_url = (
            "https://api-m.sandbox.paypal.com"
            if self.mode == "sandbox"
            else "https://api-m.paypal.com"
        )
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

    async def create_order(self, game_id: str, title: str, price: float) -> str:
        """Create a new PayPal order specifically for a GameHub purchase."""
        token = await self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Format price to 2 decimal places
        formatted_price = f"{float(price):.2f}"

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(game_id),
                    "description": title[:127], # PayPal limits description length
                    "amount": {
                        "currency_code": "USD",
                        "value": formatted_price,
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
                data = response.json()
                return data.get("id")
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
                data = response.json()
                
                # Extract required return info: success, payer, amount, transaction id
                status = data.get("status")
                success = status == "COMPLETED"
                
                payer_info = data.get("payer", {})
                payer_name = f"{payer_info.get('name', {}).get('given_name', '')} {payer_info.get('name', {}).get('surname', '')}".strip()
                
                purchase_units = data.get("purchase_units", [])
                transaction_id = None
                amount = "0.00"
                
                if purchase_units and purchase_units[0].get("payments", {}).get("captures"):
                    capture = purchase_units[0]["payments"]["captures"][0]
                    transaction_id = capture.get("id")
                    amount = capture.get("amount", {}).get("value")
                
                return {
                    "success": success,
                    "payer": payer_name or payer_info.get("email_address"),
                    "amount": amount,
                    "transaction_id": transaction_id,
                }

            except httpx.HTTPError as e:
                logger.error(f"Failed to capture PayPal order: {e}")
                raise Exception("Failed to capture PayPal order") from e

paypal_service = PayPalService()

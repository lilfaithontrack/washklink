import httpx
import logging
from typing import Dict, Any
from app.services.payment_gateways.base_payment import BasePaymentGateway

logger = logging.getLogger(__name__)

class TelebirrPaymentGateway(BasePaymentGateway):
    def __init__(self, app_id: str, app_key: str, base_url: str = "https://api.telebirr.com"):
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = base_url

    async def initiate_payment(self, amount: float, order_id: int, return_url: str = None) -> Dict[str, Any]:
        """Initiate Telebirr payment"""
        # Implement Telebirr payment initiation logic
        # This is a placeholder - you'll need to implement according to Telebirr's API
        payload = {
            "appId": self.app_id,
            "appKey": self.app_key,
            "amount": amount,
            "orderId": f"order_{order_id}",
            "returnUrl": return_url,
            "notifyUrl": f"{return_url}/api/v1/payments/telebirr/callback" if return_url else None
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payment/initiate",
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Telebirr payment initiation failed: {e}")
            raise Exception(f"Payment initiation failed: {str(e)}")

    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify Telebirr payment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/payment/verify/{transaction_id}",
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Telebirr payment verification failed: {e}")
            raise Exception(f"Payment verification failed: {str(e)}")

    async def handle_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telebirr callback"""
        return {
            "status": callback_data.get("status"),
            "transaction_id": callback_data.get("transactionId"),
            "amount": callback_data.get("amount"),
            "reference": callback_data.get("reference")
        }
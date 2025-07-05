import httpx
import logging
from typing import Dict, Any
from app.services.payment_gateways.base_payment import BasePaymentGateway

logger = logging.getLogger(__name__)

class ChapaPaymentGateway(BasePaymentGateway):
    def __init__(self, secret_key: str, base_url: str = "https://api.chapa.co/v1"):
        self.secret_key = secret_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }

    async def initiate_payment(self, amount: float, order_id: int, return_url: str = None) -> Dict[str, Any]:
        """Initiate Chapa payment"""
        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": "customer@example.com",  # You should get this from user data
            "first_name": "Customer",  # You should get this from user data
            "last_name": "Name",  # You should get this from user data
            "phone_number": "0911000000",  # You should get this from user data
            "tx_ref": f"order_{order_id}_{int(time.time())}",
            "callback_url": f"{return_url}/api/v1/payments/chapa/callback" if return_url else None,
            "return_url": return_url,
            "customization": {
                "title": "Laundry Service Payment",
                "description": f"Payment for order #{order_id}"
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/transaction/initialize",
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Chapa payment initiation failed: {e}")
            raise Exception(f"Payment initiation failed: {str(e)}")

    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify Chapa payment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transaction/verify/{transaction_id}",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Chapa payment verification failed: {e}")
            raise Exception(f"Payment verification failed: {str(e)}")

    async def handle_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Chapa callback"""
        # Process the callback data according to Chapa's webhook format
        return {
            "status": callback_data.get("status"),
            "transaction_id": callback_data.get("trx_ref"),
            "amount": callback_data.get("amount"),
            "reference": callback_data.get("reference")
        }
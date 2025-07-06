import httpx
import logging
import time
from typing import Dict, Any
from services.payment_gateways.base_payment import BasePaymentGateway

logger = logging.getLogger(__name__)

class ChapaPaymentGateway(BasePaymentGateway):
    def __init__(self, secret_key: str, base_url: str = "https://api.chapa.co/v1"):
        self.secret_key = secret_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }

    async def initiate_payment(self, amount: float, order_id: int, return_url: str = None, customer_data: Dict = None) -> Dict[str, Any]:
        """Initiate Chapa payment"""
        # Default customer data if not provided
        if not customer_data:
            customer_data = {
                "email": "customer@example.com",
                "first_name": "Customer",
                "last_name": "Name",
                "phone_number": "0911000000"
            }

        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": customer_data.get("email", "customer@example.com"),
            "first_name": customer_data.get("first_name", "Customer"),
            "last_name": customer_data.get("last_name", "Name"),
            "phone_number": customer_data.get("phone_number", "0911000000"),
            "tx_ref": f"order_{order_id}_{int(time.time())}",
            "callback_url": f"{return_url}/api/v1/payments/chapa/callback" if return_url else None,
            "return_url": return_url,
            "customization": {
                "title": "Laundry Service Payment",
                "description": f"Payment for order #{order_id}",
                "logo": "https://your-logo-url.com/logo.png"
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
                data = response.json()
                
                if data.get("status") == "success":
                    return {
                        "status": "success",
                        "payment_url": data.get("data", {}).get("checkout_url"),
                        "transaction_reference": payload["tx_ref"],
                        "message": "Payment initiated successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "message": data.get("message", "Payment initiation failed")
                    }
                    
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
                data = response.json()
                
                if data.get("status") == "success":
                    payment_data = data.get("data", {})
                    return {
                        "status": "success",
                        "payment_status": payment_data.get("status"),
                        "amount": payment_data.get("amount"),
                        "currency": payment_data.get("currency"),
                        "reference": payment_data.get("reference"),
                        "tx_ref": payment_data.get("tx_ref")
                    }
                else:
                    return {
                        "status": "error",
                        "message": data.get("message", "Payment verification failed")
                    }
                    
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
            "reference": callback_data.get("reference"),
            "currency": callback_data.get("currency", "ETB")
        }
import httpx
import logging
import time
import hashlib
import json
from typing import Dict, Any
from services.payment_gateways.base_payment import BasePaymentGateway

logger = logging.getLogger(__name__)

class TelebirrPaymentGateway(BasePaymentGateway):
    def __init__(self, app_id: str, app_key: str, base_url: str = "https://196.188.120.3:38443/apiaccess"):
        self.app_id = app_id
        self.app_key = app_key
        self.base_url = base_url

    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Generate signature for Telebirr API"""
        # Sort the data by keys and create a string
        sorted_data = sorted(data.items())
        data_string = "&".join([f"{k}={v}" for k, v in sorted_data])
        
        # Add app key and create hash
        sign_string = data_string + "&key=" + self.app_key
        signature = hashlib.sha256(sign_string.encode()).hexdigest().upper()
        
        return signature

    async def initiate_payment(self, amount: float, order_id: int, return_url: str = None, customer_data: Dict = None) -> Dict[str, Any]:
        """Initiate Telebirr payment"""
        if not customer_data:
            customer_data = {
                "phone_number": "0911000000"
            }

        # Prepare payment data
        payment_data = {
            "appId": self.app_id,
            "outTradeNo": f"order_{order_id}_{int(time.time())}",
            "totalAmount": str(amount),
            "subject": f"Laundry Service Payment - Order #{order_id}",
            "body": f"Payment for laundry order #{order_id}",
            "timeoutExpress": "30m",
            "notifyUrl": f"{return_url}/api/v1/payments/telebirr/callback" if return_url else "",
            "returnUrl": return_url or "",
            "nonce": str(int(time.time() * 1000))
        }

        # Generate signature
        payment_data["sign"] = self._generate_signature(payment_data)

        try:
            async with httpx.AsyncClient(verify=False) as client:  # Telebirr often uses self-signed certs
                response = await client.post(
                    f"{self.base_url}/payment/v1/web",
                    json=payment_data,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "0":
                    return {
                        "status": "success",
                        "payment_url": data.get("data", {}).get("toPayUrl"),
                        "transaction_reference": payment_data["outTradeNo"],
                        "message": "Payment initiated successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "message": data.get("msg", "Payment initiation failed")
                    }

        except httpx.HTTPError as e:
            logger.error(f"Telebirr payment initiation failed: {e}")
            raise Exception(f"Payment initiation failed: {str(e)}")

    async def verify_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Verify Telebirr payment"""
        query_data = {
            "appId": self.app_id,
            "outTradeNo": transaction_id,
            "nonce": str(int(time.time() * 1000))
        }

        # Generate signature
        query_data["sign"] = self._generate_signature(query_data)

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    f"{self.base_url}/payment/v1/query",
                    json=query_data,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "0":
                    payment_info = data.get("data", {})
                    return {
                        "status": "success",
                        "payment_status": payment_info.get("tradeStatus"),
                        "amount": payment_info.get("totalAmount"),
                        "currency": "ETB",
                        "reference": payment_info.get("transactionNo"),
                        "out_trade_no": payment_info.get("outTradeNo")
                    }
                else:
                    return {
                        "status": "error",
                        "message": data.get("msg", "Payment verification failed")
                    }

        except httpx.HTTPError as e:
            logger.error(f"Telebirr payment verification failed: {e}")
            raise Exception(f"Payment verification failed: {str(e)}")

    async def handle_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telebirr callback"""
        return {
            "status": callback_data.get("tradeStatus"),
            "transaction_id": callback_data.get("outTradeNo"),
            "amount": callback_data.get("totalAmount"),
            "reference": callback_data.get("transactionNo"),
            "currency": "ETB"
        }
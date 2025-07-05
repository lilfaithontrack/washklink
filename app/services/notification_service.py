import httpx
import logging
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class NotificationService:
    def __init__(self):
        self.settings = get_settings()

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS notification using AfroMessage API"""
        params = {
            "from": self.settings.AFRO_MESSAGE_IDENTIFIER_ID,
            "sender": self.settings.AFRO_MESSAGE_SENDER_NAME,
            "to": phone_number,
            "message": message,
        }

        headers = {
            "Authorization": f"Bearer {self.settings.AFRO_MESSAGE_API_KEY}"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.AFRO_MESSAGE_BASE_URL}/send",
                    headers=headers,
                    json=params,
                    timeout=10
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            logger.error(f"SMS sending failed: {e}")
            return False

    async def send_order_confirmation(self, phone_number: str, order_id: int):
        """Send order confirmation SMS"""
        message = f"Your laundry order #{order_id} has been confirmed. We'll notify you when it's ready for pickup."
        return await self.send_sms(phone_number, message)

    async def send_order_ready(self, phone_number: str, order_id: int):
        """Send order ready notification"""
        message = f"Great news! Your laundry order #{order_id} is ready for pickup. Thank you for choosing our service!"
        return await self.send_sms(phone_number, message)

    async def send_driver_assigned(self, phone_number: str, order_id: int, driver_name: str):
        """Send driver assignment notification"""
        message = f"Driver {driver_name} has been assigned to your order #{order_id}. They will contact you shortly."
        return await self.send_sms(phone_number, message)

notification_service = NotificationService()
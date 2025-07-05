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
        message = f"Your laundry order #{order_id} has been confirmed. We'll notify you when it's assigned to a service provider."
        return await self.send_sms(phone_number, message)

    async def send_order_assignment_to_provider(self, phone_number: str, order_id: int):
        """Send order assignment notification to provider"""
        message = f"New order #{order_id} has been assigned to you. Please check your dashboard to accept or reject."
        return await self.send_sms(phone_number, message)

    async def send_order_accepted(self, phone_number: str, order_id: int, provider_name: str):
        """Send order acceptance notification to customer"""
        message = f"Great news! Your order #{order_id} has been accepted by {provider_name}. We'll update you on the progress."
        return await self.send_sms(phone_number, message)

    async def send_order_ready(self, phone_number: str, order_id: int):
        """Send order ready notification"""
        message = f"Great news! Your laundry order #{order_id} is ready for pickup. Thank you for choosing our service!"
        return await self.send_sms(phone_number, message)

    async def send_driver_assigned(self, phone_number: str, order_id: int, driver_name: str):
        """Send driver assignment notification"""
        message = f"Driver {driver_name} has been assigned to your order #{order_id}. They will contact you shortly for delivery."
        return await self.send_sms(phone_number, message)

    async def send_order_out_for_delivery(self, phone_number: str, order_id: int):
        """Send out for delivery notification"""
        message = f"Your order #{order_id} is out for delivery. You should receive it within the estimated time."
        return await self.send_sms(phone_number, message)

    async def send_order_delivered(self, phone_number: str, order_id: int):
        """Send order delivered notification"""
        message = f"Your order #{order_id} has been delivered successfully. Thank you for using our service!"
        return await self.send_sms(phone_number, message)

    async def send_order_cancelled(self, phone_number: str, order_id: int, reason: str = ""):
        """Send order cancellation notification"""
        message = f"Your order #{order_id} has been cancelled. {reason}. Contact support if you have questions."
        return await self.send_sms(phone_number, message)

    async def send_status_update(self, phone_number: str, order_id: int, status: str, message: str = ""):
        """Send generic status update"""
        base_message = f"Order #{order_id} status update: {status}."
        if message:
            base_message += f" {message}"
        return await self.send_sms(phone_number, base_message)

notification_service = NotificationService()
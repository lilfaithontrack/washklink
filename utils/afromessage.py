import httpx
from models.config import get_settings
import logging

logger = logging.getLogger(__name__)

def send_otp(mobile: str, otp: str) -> dict:
    settings = get_settings()

    if not mobile:
        return {
            "ResponseCode": "401",
            "Result": "false",
            "ResponseMsg": "Mobile number is required!"
        }

    message = f"Your OTP is {otp}. It will expire in 5 minutes."

    payload = {
        "from": settings.AFRO_MESSAGE_IDENTIFIER_ID,
        "sender": settings.AFRO_MESSAGE_SENDER_NAME,
        "to": mobile,
        "text": message,
    }

    headers = {
        "Authorization": f"Bearer {settings.AFRO_MESSAGE_API_KEY}"
    }

    try:
        response = httpx.post(
            f"{settings.AFRO_MESSAGE_BASE_URL}/send-sms",  # Adjust endpoint as needed
            headers=headers,
            data=payload,
            timeout=10
        )
        response.raise_for_status()
        return {
            "ResponseCode": "200",
            "Result": "true",
            "ResponseMsg": "OTP sent successfully!"
        }
    except httpx.HTTPError as e:
        logger.error(f"OTP sending failed: {e}")
        return {
            "ResponseCode": "500",
            "Result": "false",
            "ResponseMsg": f"HTTP error occurred: {str(e)}"
        }


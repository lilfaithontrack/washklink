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

    params = {
        "from": settings.AFRO_MESSAGE_IDENTIFIER_ID,
        "sender": settings.AFRO_MESSAGE_SENDER_NAME,
        "to": mobile,
        "ps": otp,  # OTP passed here
        "sb": settings.AFRO_MESSAGE_SB,
        "sa": settings.AFRO_MESSAGE_SA,
        "ttl": settings.AFRO_MESSAGE_TTL,
        "len": settings.AFRO_MESSAGE_LEN,
        "t": settings.AFRO_MESSAGE_T,
        "callback": settings.AFRO_MESSAGE_CALLBACK,
    }

    headers = {
        "Authorization": f"Bearer {settings.AFRO_MESSAGE_API_KEY}"
    }

    try:
        response = httpx.get(
            f"{settings.AFRO_MESSAGE_BASE_URL}/challenge",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            return {
                "ResponseCode": "500",
                "Result": "false",
                "ResponseMsg": "Invalid JSON response from OTP provider"
            }

        if data.get("acknowledge") == "success":
            return {
                "ResponseCode": "200",
                "Result": "true",
                "ResponseMsg": "Check your message!"
            }
        else:
            return {
                "ResponseCode": "400",
                "Result": "false",
                "ResponseMsg": data.get("ResponseMsg", "OTP sending failed")
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while sending OTP: {e}")
        return {
            "ResponseCode": str(e.response.status_code),
            "Result": "false",
            "ResponseMsg": f"HTTP error: {e.response.text}"
        }
    except Exception as e:
        logger.error(f"Unexpected error while sending OTP: {e}")
        return {
            "ResponseCode": "500",
            "Result": "false",
            "ResponseMsg": f"Unexpected error: {str(e)}"
        }

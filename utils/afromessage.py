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

    # Compose the SMS text message
    message = f"Your OTP is {otp}. It will expire in 5 minutes."

    # Payload for the SMS API
    payload = {
        "from": settings.AFRO_MESSAGE_IDENTIFIER_ID,
        "sender": settings.AFRO_MESSAGE_SENDER_NAME,
        "to": mobile,
        "text": message
    }

    headers = {
        "Authorization": f"Bearer {settings.AFRO_MESSAGE_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        # Make the POST request to send the SMS
        response = httpx.post(
            f"{settings.AFRO_MESSAGE_BASE_URL}/send-sms",  # Replace with the correct endpoint if different
            data=payload,
            headers=headers,
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

        # Check provider-specific response structure
        if data.get("acknowledge") == "success" or data.get("Result") == "true":
            return {
                "ResponseCode": "200",
                "Result": "true",
                "ResponseMsg": "OTP sent successfully"
            }
        else:
            return {
                "ResponseCode": "400",
                "Result": "false",
                "ResponseMsg": data.get("ResponseMsg", "OTP sending failed")
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error while sending OTP: {str(e)}")
        return {
            "ResponseCode": str(e.response.status_code),
            "Result": "false",
            "ResponseMsg": f"HTTP error: {e.response.text}"
        }
    except Exception as e:
        logger.error(f"Unexpected error while sending OTP: {str(e)}")
        return {
            "ResponseCode": "500",
            "Result": "false",
            "ResponseMsg": f"Unexpected error: {str(e)}"
        }

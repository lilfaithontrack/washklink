import httpx
from models.config import get_settings
import logging

logger = logging.getLogger(__name__)

def send_otp(mobile: str) -> dict:
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
        "ps": "",
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
                "ResponseCode": "200",
                "Result": "false",
                "ResponseMsg": "Please try again!"
            }

    except httpx.HTTPError as e:
        logger.error(f"OTP sending failed: {e}")
        return {
            "ResponseCode": "500",
            "Result": "false",
            "ResponseMsg": f"HTTP error occurred: {str(e)}"
        }


def verify_otp(mobile: str, otp_code: str) -> bool:
    """
    Verify OTP code with AfroMessage API.
    Returns True if valid, False otherwise.
    """
    settings = get_settings()

    if not mobile or not otp_code:
        logger.warning("Mobile number and OTP code are required for verification")
        return False

    params = {
        "from": settings.AFRO_MESSAGE_IDENTIFIER_ID,
        "sender": settings.AFRO_MESSAGE_SENDER_NAME,
        "to": mobile,
        "challenge_response": otp_code,  # The OTP code provided by user
        "sb": settings.AFRO_MESSAGE_SB,
        "sa": settings.AFRO_MESSAGE_SA,
    }

    headers = {
        "Authorization": f"Bearer {settings.AFRO_MESSAGE_API_KEY}"
    }

    try:
        response = httpx.get(
            f"{settings.AFRO_MESSAGE_BASE_URL}/challenge/verify",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            logger.error("Invalid JSON response from OTP verification")
            return False

        # AfroMessage usually returns acknowledge 'success' for valid OTP
        if data.get("acknowledge") == "success":
            return True
        else:
            logger.info(f"OTP verification failed: {data}")
            return False

    except httpx.HTTPError as e:
        logger.error(f"OTP verification failed: {e}")
        return False

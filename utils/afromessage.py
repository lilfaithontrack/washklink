import httpx
import os
import requests
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


def verify_otp(to: str, code: str) -> bool:
    token = os.getenv("AFRO_MESSAGE_API_KEY")  # Make sure this env var is set with your API key
    base_url = 'https://api.afromessage.com/api/verify'
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{base_url}?to={to}&code={code}'

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('acknowledge') == 'success':
                return True
            else:
                logger.warning(f"OTP verification failed: {data}")
                return False
        else:
            logger.error(f"HTTP error verifying OTP: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception during OTP verification: {e}")
        return False

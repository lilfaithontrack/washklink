# sms_utils.py
import requests
import random
from config import get_settings

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    settings = get_settings()

    payload = {
        "receiver": phone_number,
        "message": f"Your OTP code is: {otp_code}",
        "sender_name": settings.AFRO_MESSAGE_SENDER_NAME,
    }

    if settings.AFRO_MESSAGE_IDENTIFIER_ID:
        payload["identifier"] = settings.AFRO_MESSAGE_IDENTIFIER_ID

    headers = {
        "apiKey": settings.AFRO_MESSAGE_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{settings.AFRO_MESSAGE_BASE_URL}/send",
        json=payload,
        headers=headers
    )

    return response.status_code == 200

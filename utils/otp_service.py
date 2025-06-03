import requests
import random
import time
from typing import Dict
from models.config import get_settings

# Temporary in-memory store
otp_store: Dict[str, Dict[str, float]] = {}

# OTP valid for 5 minutes
OTP_EXPIRY = 300  # seconds

def generate_otp() -> str:
    """Generate a 6-digit numeric OTP"""
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    """Send OTP via AfroMessage SMS API"""
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

    try:
        response = requests.post(
            f"{settings.AFRO_MESSAGE_BASE_URL}/send",
            json=payload,
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except requests.RequestException:
        return False

def save_otp(phone_number: str, otp: str):
    """Save OTP with timestamp for later verification"""
    otp_store[phone_number] = {
        "otp": otp,
        "timestamp": time.time()
    }

def verify_otp(phone_number: str, otp: str) -> bool:
    """Verify OTP: must exist, match, and not be expired"""
    data = otp_store.get(phone_number)
    if not data:
        return False

    if time.time() - data["timestamp"] > OTP_EXPIRY:
        otp_store.pop(phone_number, None)
        return False

    if data["otp"] == otp:
        otp_store.pop(phone_number, None)
        return True

    return False

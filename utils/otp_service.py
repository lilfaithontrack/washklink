import requests
import random
import time
from typing import Dict
from core.config import get_settings

# Temporary in-memory store
otp_store: Dict[str, Dict[str, float]] = {}

# OTP valid for 5 minutes
OTP_EXPIRY = 300  # seconds

def generate_otp() -> str:
    """Generate a 6-digit numeric OTP"""
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    """Send OTP via AfroMessage SMS API - matches working PHP implementation"""
    settings = get_settings()
    
    # Use the complete token from your working PHP code
    token = "eyJhbGciOiJIUzI1NiJ9.eyJpZGVudGlmaWVyIjoidWp3V1dYNWlDRU81ZkE4TjczQ3NKN29Jek52YlRodWMiLCJleHAiOjE4ODYxNTU5MzksImlhdCI6MTcyODM4OTUzOSwianRpIjoiNWMzMWE2OTYtYjNhNi00NWVkLTk3ZmUtYTk4ZGZmY2ZiYWJmIn0._0QVF8dLEkS0TQKEe8JHtXxqoe8D1YcrKG7mgEPviHI"
    
    # Parameters from your working PHP code
    from_id = "e80ad9d8-adf3-463f-80f4-7c4b39f7f164"
    sender = "Endode"
    to = phone_number
    callback = ""
    sb = 0
    sa = 0
    ttl = 0
    len_param = 6
    t = 0
    
    # Build URL with query parameters like PHP code
    url = f"{settings.AFRO_MESSAGE_BASE_URL}/challenge"
    params = {
        "from": from_id,
        "sender": sender,
        "to": to,
        "ps": "",  # post parameter (URL encoded)
        "sb": sb,
        "sa": sa,
        "ttl": ttl,
        "len": len_param,
        "t": t,
        "callback": callback
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
    }

    try:
        print(f"📱 Sending SMS to {phone_number} using challenge endpoint")
        print(f"🔗 URL: {url}")
        print(f"📦 Params: {params}")
        
        # Use GET method with query parameters like PHP
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            # Check acknowledge field like PHP code
            try:
                data = response.json()
                if data.get('acknowledge') == 'success':
                    print(f"✅ SMS sent successfully to {phone_number}")
                    return True
                else:
                    print(f"❌ SMS failed: {data}")
                    return False
            except Exception as e:
                print(f"❌ Error parsing response: {e}")
                return False
        else:
            print(f"❌ SMS failed with status {response.status_code}: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ SMS sending error: {str(e)}")
        return False

def save_otp(phone_number: str, otp: str):
    """Save OTP with timestamp for later verification"""
    # Clean and normalize inputs
    phone_number = str(phone_number).strip()
    otp = str(otp).strip()
    
    print(f"💾 Saving OTP: '{otp}' (len={len(otp)}) for phone: '{phone_number}'")
    otp_store[phone_number] = {
        "otp": otp,
        "timestamp": time.time()
    }
    print(f"✅ OTP saved. Store now contains: {otp_store}")

def verify_otp(phone_number: str, otp: str) -> bool:
    """Verify OTP: must exist, match, and not be expired"""
    # Clean and normalize inputs
    phone_number = str(phone_number).strip()
    otp = str(otp).strip()
    
    print(f"🔍 Verifying OTP: '{otp}' (len={len(otp)}) for phone: '{phone_number}'")
    print(f"📊 OTP Store contents: {otp_store}")
    
    data = otp_store.get(phone_number)
    if not data:
        print(f"❌ No OTP data found for phone: '{phone_number}'")
        print(f"📋 Available phone numbers: {list(otp_store.keys())}")
        return False

    current_time = time.time()
    time_diff = current_time - data["timestamp"]
    print(f"⏰ Time diff: {time_diff:.2f}s, Expiry: {OTP_EXPIRY}s")
    
    if time_diff > OTP_EXPIRY:
        print(f"❌ OTP expired for phone: '{phone_number}' (expired {time_diff-OTP_EXPIRY:.2f}s ago)")
        otp_store.pop(phone_number, None)
        return False

    stored_otp = str(data["otp"]).strip()
    print(f"🔍 Comparing: stored='{stored_otp}' (len={len(stored_otp)}) vs provided='{otp}' (len={len(otp)})")
    print(f"🔍 Types: stored={type(stored_otp)} vs provided={type(otp)}")
    
    if stored_otp == otp:
        print(f"✅ OTP match successful for phone: '{phone_number}'")
        otp_store.pop(phone_number, None)
        return True
    else:
        print(f"❌ OTP mismatch for phone: '{phone_number}'")
        print(f"   Stored: '{stored_otp}' (bytes: {stored_otp.encode()})")
        print(f"   Provided: '{otp}' (bytes: {otp.encode()})")
        return False

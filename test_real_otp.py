#!/usr/bin/env python3
"""
Test Real OTP Verification
Use this to test with the actual OTP you received on your phone
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"
PHONE_NUMBER = "+251951521621"
OTP_FROM_PHONE = "128332"  # The OTP you received on your phone

def test_real_otp_verification():
    print("🧪 Testing Real OTP Verification")
    print("=" * 50)
    print(f"📱 Phone: {PHONE_NUMBER}")
    print(f"🔢 OTP from phone: {OTP_FROM_PHONE}")
    
    # Verify the OTP you received on your phone
    verify_data = {
        "phone_number": PHONE_NUMBER,
        "otp_code": OTP_FROM_PHONE,
        "full_name": "Real User Test"
    }
    
    try:
        print(f"\n✅ Verifying OTP: {OTP_FROM_PHONE}")
        verify_response = requests.post(f"{BASE_URL}/verify-otp", json=verify_data)
        print(f"Verify Status: {verify_response.status_code}")
        print(f"Verify Response: {verify_response.text}")
        
        if verify_response.status_code == 200:
            print("🎉 Real OTP verification successful!")
            data = verify_response.json()
            if 'access_token' in data:
                print(f"🔑 Access token received: {data['access_token'][:50]}...")
            if 'user' in data:
                print(f"👤 User created/logged in: {data['user']}")
        else:
            print("❌ Real OTP verification failed!")
            try:
                error_data = verify_response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw error: {verify_response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Real OTP Testing Script")
    print("Testing with the OTP you actually received on your phone")
    print()
    
    test_real_otp_verification()
#!/usr/bin/env python3
"""
Request Fresh OTP
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"
PHONE_NUMBER = "+251951521621"

def request_fresh_otp():
    print(f"📱 Requesting fresh OTP for {PHONE_NUMBER}...")
    
    request_data = {"phone_number": PHONE_NUMBER}
    
    try:
        response = requests.post(f"{BASE_URL}/request-otp", json=request_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Fresh OTP requested successfully!")
            print("📱 Check your phone for the new OTP")
            
            # Prompt for the new OTP
            print("\n" + "="*50)
            print("Enter the NEW OTP you just received:")
            new_otp = input("OTP: ").strip()
            
            if new_otp:
                # Test verification immediately
                verify_data = {
                    "phone_number": PHONE_NUMBER,
                    "otp_code": new_otp,
                    "full_name": "Fresh OTP Test"
                }
                
                print(f"\n✅ Testing verification with OTP: {new_otp}")
                verify_response = requests.post(f"{BASE_URL}/verify-otp", json=verify_data)
                print(f"Verify Status: {verify_response.status_code}")
                
                if verify_response.status_code == 200:
                    print("🎉 SUCCESS! OTP verification worked!")
                    data = verify_response.json()
                    print(f"User: {data.get('user', {}).get('full_name')}")
                    print(f"Token: {data.get('access_token', '')[:50]}...")
                else:
                    print("❌ Verification failed")
                    print(f"Error: {verify_response.text}")
            
        else:
            print("❌ Failed to request OTP")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    request_fresh_otp()
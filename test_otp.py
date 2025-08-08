#!/usr/bin/env python3
"""
Quick OTP Test Script
Run this to test the OTP functionality directly without going through the mobile app.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1/auth"
PHONE_NUMBER = "+251951521621"  # User's actual phone number

def test_otp_flow():
    print("🧪 Testing OTP Flow")
    print("=" * 50)
    
    # Step 1: Request OTP
    print(f"📱 Requesting OTP for {PHONE_NUMBER}...")
    request_data = {"phone_number": PHONE_NUMBER}
    
    try:
        response = requests.post(f"{BASE_URL}/request-otp", json=request_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            otp_code = data.get("otp")
            print(f"✅ OTP Generated: {otp_code}")
            
            # Step 2: Check OTP store
            print("\n🔍 Checking OTP store...")
            debug_response = requests.get(f"{BASE_URL}/debug/otp-store")
            if debug_response.status_code == 200:
                store_data = debug_response.json()
                print(f"Store contents: {json.dumps(store_data, indent=2)}")
            
            # Step 3: Verify OTP
            print(f"\n✅ Verifying OTP: {otp_code}")
            verify_data = {
                "phone_number": PHONE_NUMBER,
                "otp_code": otp_code,
                "full_name": "Test User"
            }
            
            verify_response = requests.post(f"{BASE_URL}/verify-otp", json=verify_data)
            print(f"Verify Status: {verify_response.status_code}")
            print(f"Verify Response: {verify_response.text}")
            
            if verify_response.status_code == 200:
                print("🎉 OTP verification successful!")
            else:
                print("❌ OTP verification failed!")
                
        else:
            print("❌ Failed to request OTP")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_otp_store():
    """Check what's currently in the OTP store"""
    print("\n🔍 Checking current OTP store contents...")
    try:
        response = requests.get(f"{BASE_URL}/debug/otp-store")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed to get store data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("OTP Testing Script")
    print("Make sure your backend is running on localhost:8000")
    print()
    
    # Test the full flow
    test_otp_flow()
    
    # Check store after test
    check_otp_store()
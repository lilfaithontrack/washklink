# main.py or routers/users.py

import time
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token
from google.auth.transport import requests

# Make sure these paths are correct for your project structure
from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse, UserUpdate # UserUpdate might not be used, but good to have
from utils.otp_service import generate_otp, otp_store
from utils.afromessage import send_otp as send_afro_otp


router = APIRouter(prefix="/users", tags=["Users"])

GOOGLE_CLIENT_ID = "1038087912249-85n553k9b73khia51v7doc6orsau9nov.apps.googleusercontent.com"

# ==============================================================================
# --- DEPENDENCIES ---
# ==============================================================================

# 1. Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Authentication Dependency (Placeholder)
async def get_current_user_placeholder(db: Session = Depends(get_db)):
    """
    ### CRITICAL: THIS IS A PLACEHOLDER. ###
    In a real application, this function must:
    1. Extract the JWT token from the 'Authorization: Bearer <token>' header.
    2. Decode the token to get a unique user identifier (e.g., user_id or email).
    3. Fetch the user from the database using that identifier.
    4. Raise an HTTPException if the token is invalid or the user doesn't exist.

    For now, it simulates a logged-in user by fetching the user with ID=1.
    """
    user = db.query(DBUser).filter(DBUser.id == 1).first() 
    if user is None:
        # This will happen if you don't have a user with ID=1 in your database.
        # Create one manually or adjust the ID to test.
        raise HTTPException(status_code=401, detail="User not authenticated (placeholder logic)")
    return user

# ==============================================================================
# --- PYDANTIC MODELS (SCHEMAS) ---
# ==============================================================================

class PhoneOnlyRequest(BaseModel):
    phone_number: str

class VerifyLoginRequest(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str | None = None
    email: EmailStr | None = None

class GoogleAuthRequest(BaseModel):
    id_token: str

class VerifyPhoneAndUpdateProfileRequest(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str | None = None

# ==============================================================================
# --- 1. PHONE LOGIN & SIGNUP FLOW ---
# ==============================================================================

@router.post("/request-login-otp", summary="Request OTP for Login/Signup")
def request_login_otp(data: PhoneOnlyRequest, db: Session = Depends(get_db)):
    otp = generate_otp()
    otp_store[data.phone_number] = json.dumps({
        "otp": otp,
        "action": "verify_login",
        "expires_at": time.time() + 300
    })
    result = send_afro_otp(data.phone_number)
    if result.get("Result") != "true":
        raise HTTPException(status_code=500, detail=result.get("ResponseMsg", "Failed to send OTP"))
    return {"message": "OTP for login sent successfully"}

@router.post("/verify-login-otp", response_model=UserResponse, summary="Verify OTP and Login/Signup")
def verify_login_otp(data: VerifyLoginRequest, db: Session = Depends(get_db)):
    otp_entry_raw = otp_store.get(data.phone_number)
    if not otp_entry_raw:
        raise HTTPException(status_code=400, detail="OTP not found or has expired. Please request a new one.")
    try:
        otp_entry = json.loads(otp_entry_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Server error: Corrupted OTP format.")

    if (otp_entry.get("otp") != data.otp_code or otp_entry.get("action") != "verify_login"):
        raise HTTPException(status_code=400, detail="Invalid OTP or action. Please try again.")
    if otp_entry.get("expires_at", 0) < time.time():
        raise HTTPException(status_code=400, detail="Expired OTP. Please request a new one.")

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        user = DBUser(phone_number=data.phone_number, full_name=data.full_name or "", email=data.email or None)
        db.add(user)
        db.commit()
        db.refresh(user)

    otp_store.pop(data.phone_number, None)
    return user

# ==============================================================================
# --- 2. GOOGLE OAUTH2 FLOW ---
# ==============================================================================

@router.post("/google-auth", response_model=UserResponse, summary="Authenticate with Google")
def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        info = id_token.verify_oauth2_token(data.id_token, requests.Request(), GOOGLE_CLIENT_ID)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google token")

    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        user = DBUser(full_name=info.get("name"), email=email, phone_number=None) # phone_number is null
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

# ==============================================================================
# --- 3. PROFILE & PHONE MANAGEMENT FLOW (AUTHENTICATED) ---
# ==============================================================================

@router.post("/profile/request-phone-verification", summary="Request OTP to Add/Update Phone (Auth Required)")
def request_phone_verification_otp(
    data: PhoneOnlyRequest, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user_placeholder)
):
    new_phone_number = data.phone_number
    existing_user_with_phone = db.query(DBUser).filter(DBUser.phone_number == new_phone_number).first()
    if existing_user_with_phone and existing_user_with_phone.id != current_user.id:
        raise HTTPException(status_code=409, detail="Phone number is already in use by another account.")

    otp = generate_otp()
    otp_store[new_phone_number] = json.dumps({
        "otp": otp,
        "action": "verify_phone_for_user",
        "user_id": current_user.id,
        "expires_at": time.time() + 300
    })

    result = send_afro_otp(new_phone_number)
    if result.get("Result") != "true":
        raise HTTPException(status_code=500, detail=result.get("ResponseMsg", "Failed to send OTP"))
    return {"message": f"OTP sent to {new_phone_number} for verification."}

@router.put("/profile/verify-and-update", response_model=UserResponse, summary="Verify Phone & Update Profile (Auth Required)")
def verify_phone_and_update_profile(
    data: VerifyPhoneAndUpdateProfileRequest, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user_placeholder)
):
    otp_entry_raw = otp_store.get(data.phone_number)
    if not otp_entry_raw:
        raise HTTPException(status_code=400, detail="OTP not found or has expired.")
    try:
        otp_entry = json.loads(otp_entry_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Server error.")

    if otp_entry.get("expires_at", 0) < time.time():
        raise HTTPException(status_code=400, detail="Expired OTP. Please request a new one.")

    if (
        otp_entry.get("otp") != data.otp_code or
        otp_entry.get("action") != "verify_phone_for_user" or
        otp_entry.get("user_id") != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")

    current_user.phone_number = data.phone_number
    if data.full_name:
        current_user.full_name = data.full_name
    
    db.commit()
    db.refresh(current_user)
    otp_store.pop(data.phone_number, None)
    return current_user

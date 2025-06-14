import time
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from google.oauth2 import id_token
from google.auth.transport import requests

from database import SessionLocal
from models.users import DBUser
from schemas.users_schema import UserResponse, UserUpdate
from utils.otp_service import generate_otp, otp_store
from utils.afromessage import send_otp as send_afro_otp

# --- SETUP ---
# The router prefix and tags remain the same.
router = APIRouter(prefix="/users", tags=["Users"])

GOOGLE_CLIENT_ID = "1038087912249-85n553k9b73khia51v7doc6orsau9nov.apps.googleusercontent.com"

# --- DATABASE DEPENDENCY ---
# This helper function to get a DB session is perfect as is.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PYDANTIC MODELS (SCHEMAS) ---
# These models define the shape of your request bodies. They are well-defined.
class UserCreate(BaseModel):
    phone_number: str

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str | None = None
    email: EmailStr | None = None

class GoogleAuthRequest(BaseModel):
    id_token: str

# ==============================================================================
# --- AUTHENTICATION FLOWS ---
# ==============================================================================

# --- 1. LOGIN / SIGNUP FLOW ---

@router.post("/request-login-otp", summary="Request OTP for Login/Signup")
def request_login_otp(data: UserCreate, db: Session = Depends(get_db)):
    """
    Generates and sends an OTP for the purpose of logging in or creating a new account.
    The OTP is marked with the action 'verify_login'.
    """
    otp = generate_otp()
    
    # Store OTP with the specific action "verify_login".
    otp_store[data.phone_number] = json.dumps({
        "otp": otp,
        "action": "verify_login",  # This OTP is for logging in
        "expires_at": time.time() + 300  # expires in 5 minutes
    })

    # Send the OTP via your messaging service
    result = send_afro_otp(data.phone_number)
    if result.get("Result") != "true":
        raise HTTPException(status_code=500, detail=result.get("ResponseMsg", "Failed to send OTP"))

    return {"message": "OTP for login sent successfully"}


@router.post("/verify-login-otp", response_model=UserResponse, summary="Verify OTP and Login/Signup")
def verify_login_otp(data: UserVerify, db: Session = Depends(get_db)):
    """
    Verifies an OTP. If valid, finds the user or creates a new one, then returns the user data.
    """
    otp_entry_raw = otp_store.get(data.phone_number)

    if not otp_entry_raw:
        raise HTTPException(status_code=400, detail="OTP not found or has expired. Please request a new one.")

    try:
        otp_entry = json.loads(otp_entry_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Server error: Corrupted OTP format.")

    # HARDENED: Stricter check. We now ensure the OTP and the action are both correct.
    if (
        otp_entry.get("otp") != data.otp_code or
        otp_entry.get("action") != "verify_login" or  # Must be a login OTP
        otp_entry.get("expires_at", 0) < time.time()
    ):
        raise HTTPException(status_code=400, detail="Invalid OTP or action. Please try again.")

    # Find user or create if they don't exist
    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        user = DBUser(
            phone_number=data.phone_number,
            full_name=data.full_name or "",
            email=data.email or None
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    otp_store.pop(data.phone_number, None)  # Remove the used OTP
    return user


# --- 2. PROFILE UPDATE FLOW ---

# NEW: This is the new, dedicated endpoint to start the profile update process.
@router.post("/request-update-otp", summary="Request OTP for Profile Update")
def request_update_otp(data: UserCreate, db: Session = Depends(get_db)):
    """
    Generates and sends an OTP for the purpose of updating an existing user's profile.
    This will fail if the user does not exist.
    """
    # First, ensure the user exists.
    user_exists = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User with this phone number not found.")

    otp = generate_otp()
    
    # Store OTP with the specific action "update_profile".
    otp_store[data.phone_number] = json.dumps({
        "otp": otp,
        "action": "update_profile",  # This OTP is for updating a profile
        "expires_at": time.time() + 300
    })

    result = send_afro_otp(data.phone_number)
    if result.get("Result") != "true":
        raise HTTPException(status_code=500, detail=result.get("ResponseMsg", "Failed to send OTP"))

    return {"message": "OTP for profile update sent successfully."}


# FIXED: The original update endpoint is now correctly named and implemented.
@router.put("/update-profile", response_model=UserResponse, summary="Verify OTP and Update Profile")
def update_profile(data: UserUpdate, db: Session = Depends(get_db)):
    """
    Verifies an OTP and, if valid, updates the user's profile information.
    """
    otp_entry_raw = otp_store.get(data.phone_number)

    if not otp_entry_raw:
        raise HTTPException(status_code=400, detail="OTP not found or has expired. Please request a new one.")

    try:
        otp_entry = json.loads(otp_entry_raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Server error: Corrupted OTP format.")

    # This check now works because the request_update_otp endpoint sets the correct action.
    if (
        otp_entry.get("otp") != data.otp_code or
        otp_entry.get("action") != "update_profile" or  # Must be an update OTP
        otp_entry.get("expires_at", 0) < time.time()
    ):
        raise HTTPException(status_code=400, detail="Invalid OTP for profile update. Please try again.")

    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        # This case is unlikely if the request-otp endpoint is used, but it's good practice.
        raise HTTPException(status_code=404, detail="User not found.")

    # Update user details from the request data
    if data.full_name:
        user.full_name = data.full_name
    
    # You can easily extend this to update other fields defined in UserUpdate schema
    # if data.email:
    #     user.email = data.email

    db.commit()
    db.refresh(user)

    otp_store.pop(data.phone_number, None)  # Remove the used OTP
    return user


# --- 3. GOOGLE OAUTH2 FLOW ---
# This flow was already well-implemented. No changes needed.
@router.post("/google-auth", response_model=UserResponse, summary="Authenticate with Google")
def google_auth(data: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        info = id_token.verify_oauth2_token(
            data.id_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = info.get("email")
    full_name = info.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google token")

    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        # Note: A user signing in with Google won't have a phone number initially.
        user = DBUser(full_name=full_name, email=email, phone_number=None)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

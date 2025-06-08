from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import requests

# Google Auth Libraries
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow

# Your project's modules
from database import SessionLocal, get_db
from models.users import DBUser
from schemas.users_schema import UserResponse
from utils.otp_service import generate_otp, send_otp_sms, otp_store

# --- Router Setup ---
router = APIRouter(prefix="/users", tags=["Users"])

# --- Pydantic Models for Requests ---
class UserCreate(BaseModel):
    phone_number: str

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str = None
    email: EmailStr = None

# This is the NEW model for the Authorization Code flow
class GoogleAuthCodeRequest(BaseModel):
    code: str

# --- OTP Endpoints (No changes needed) ---
@router.post("/request-otp")
def request_otp(data: UserCreate, db: Session = Depends(get_db)):
    otp = generate_otp()
    sent = send_otp_sms(data.phone_number, otp)
    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    otp_store[data.phone_number] = otp
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", response_model=UserResponse)
def verify_otp(data: UserVerify, db: Session = Depends(get_db)):
    # This logic is for pure OTP login.
    # For a logged-in Google user, you might want to link the phone to their account instead.
    real_otp = otp_store.get(data.phone_number)
    if real_otp != data.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    user = db.query(DBUser).filter(DBUser.phone_number == data.phone_number).first()
    if not user:
        user = DBUser(
            phone_number=data.phone_number,
            full_name=data.full_name or "",
            email=data.email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    del otp_store[data.phone_number]
    return user


### --- NEW Google Authorization Code Endpoint --- ###
# This replaces your old /google-auth endpoint.
# It receives an authorization code, gets an access token, and calls the People API.

@router.post("/google-auth-code", response_model=UserResponse)
def google_auth_code_handler(payload: GoogleAuthCodeRequest, db: Session = Depends(get_db)):
    
    # Ensure you have your client_secret.json file from Google Cloud Console
    # in the root of your project, or provide the correct path.
    # This file contains your client_id, client_secret, etc.
    try:
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=[
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid",
                "https://www.googleapis.com/auth/user.phonenumbers.read" # The crucial scope
            ],
            # This must match the authorized redirect URI in your Google Cloud setup
            redirect_uri="postmessage" 
        )
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="client_secret.json not found on server.")

    try:
        # Exchange the authorization code for credentials (access_token, id_token)
        flow.fetch_token(code=payload.code)
        credentials = flow.credentials
        
        access_token = credentials.token
        id_token_jwt = credentials.id_token

        # Verify the ID token to get basic user info
        id_info = id_token.verify_oauth2_token(id_token_jwt, google_requests.Request(), credentials.client_id)
        
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong issuer.")
            
        email = id_info['email']
        full_name = id_info.get('name')
        
        # --- Use the access token to get the phone number from the People API ---
        phone_number = None
        people_api_url = "https://people.googleapis.com/v1/people/me?personFields=phoneNumbers"
        headers = {"Authorization": f"Bearer {access_token}"}
        people_response = requests.get(people_api_url, headers=headers)
        
        if people_response.ok:
            phone_data = people_response.json().get("phoneNumbers")
            if phone_data:
                phone_number = phone_data[0].get("value")

        # --- Find user by email or Create a new user ---
        user = db.query(DBUser).filter(DBUser.email == email).first()
        
        if not user:
            # Create a new user if they don't exist
            user = DBUser(
                full_name=full_name, 
                email=email, 
                phone_number=phone_number, # Save the phone number if we got it
                is_active=True # Mark user as active
            )
            db.add(user)
        else:
            # If user exists, update their details if needed
            user.full_name = full_name
            if not user.phone_number and phone_number:
                # If they exist but didn't have a phone number, add it.
                user.phone_number = phone_number
        
        db.commit()
        db.refresh(user)

        return user

    except Exception as e:
        print(f"An error occurred during Google authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or fetch user data.",
        )

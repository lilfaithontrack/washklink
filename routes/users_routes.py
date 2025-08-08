import time
from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel, EmailStr
from typing import List, Any
from models.mongo_models import User, UserRole
from schemas.users_schema import UserResponse, UserCreate, UserUpdate
from utils.otp_service import generate_otp, send_otp_sms, save_otp, verify_otp
from datetime import datetime, timedelta
import jwt
from core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Legacy endpoints for backward compatibility
@router.post("/auth/request-otp")
async def request_otp_legacy(request_data: dict):
    """Legacy OTP request endpoint - uses new OTP service"""
    phone_number = request_data.get("phone_number")
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required"
        )
    
    try:
        # Generate OTP
        otp_code = generate_otp()
        
        # Save OTP
        save_otp(phone_number, otp_code)
        
        # Send OTP via SMS
        if send_otp_sms(phone_number, otp_code):
            logger.info(f"OTP sent successfully to {phone_number}")
            return {
                "message": "OTP sent successfully", 
                "note": "This is a legacy endpoint. Please use /api/v1/auth/request-otp for new implementations."
            }
        else:
            logger.error(f"Failed to send OTP to {phone_number}")
            # Still save the OTP for testing purposes
            return {
                "message": "OTP generated for testing", 
                "note": "SMS failed but OTP saved for testing"
            }
            
    except Exception as e:
        logger.error(f"Error requesting OTP for {phone_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )

class UserVerify(BaseModel):
    phone_number: str
    otp_code: str
    full_name: str
    email: EmailStr | None = None

@router.post("/auth/login", response_model=UserResponse)
async def login_legacy(user: UserVerify, response: Response):
    """Legacy login endpoint - OTP-based login/register for customers"""
    try:
        # Step 1: Verify OTP
        if not verify_otp(user.phone_number, user.otp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP"
            )

        # Step 2: Find or create user in MongoDB
        db_user = await User.find_one(User.phone_number == user.phone_number)

        if not db_user:
            # Create new customer user
            db_user = User(
                full_name=user.full_name,
                phone_number=user.phone_number,
                email=user.email,  # Optional for customers
                role=UserRole.USER,
                is_active=True,
            )
            await db_user.save()
            logger.info(f"New customer registered: {user.phone_number}")
        else:
            # Update existing user info if needed
            updated = False
            if user.full_name != db_user.full_name:
                db_user.full_name = user.full_name
                updated = True
            if user.email and user.email != db_user.email:
                db_user.email = user.email
                updated = True
            if updated:
                await db_user.save()

        # Update last login
        db_user.last_login = datetime.utcnow()
        await db_user.save()

        # Generate JWT token
        payload = {
            "user_id": str(db_user.id),
            "role": db_user.role,
            "is_active": db_user.is_active,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Set cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="none" if settings.COOKIE_SECURE else "lax",
            max_age=60*60*24*7,  # 7 days
            path="/"
        )

        # Step 3: Return user response
        return UserResponse(
            id=str(db_user.id),
            full_name=db_user.full_name,
            phone=db_user.phone_number,
            email=db_user.email,
            role=db_user.role,
            is_active=db_user.is_active,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in legacy login for {user.phone_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.get("/users", response_model=List[UserResponse])
async def get_all_users_legacy():
    """Legacy endpoint - MongoDB implementation"""
    try:
        users = await User.find_all().to_list()
        return [
            UserResponse(
                id=str(user.id),
                full_name=user.full_name,
                phone=user.phone_number,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            ) for user in users
        ]
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id_legacy(user_id: str):
    """Legacy endpoint - MongoDB implementation"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=str(user.id),
            full_name=user.full_name,
            phone=user.phone_number,
            email=user.email,
            role=user.role,
            is_active=user.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )
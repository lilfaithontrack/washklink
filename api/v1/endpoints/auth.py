from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from api.deps import get_current_active_user
from services.auth_service import authenticate_user, authenticate_admin_user
from schemas.auth import AdminLogin
from schemas.user import UserResponse
from models.mongo_models import User
import logging
import uuid

import jwt
from datetime import datetime, timedelta
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(redirect_slashes=False)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
) -> Any:
    try:
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = {
            "user_id": str(user.id),
            "role": user.role,
            "is_active": user.is_active,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=60*60*24*7,  # 7 days
            path="/"
        )
        logger.info(f"Successful login for user: {user.email}")
        return {
            "message": "Login successful",
            "user": UserResponse(
                id=str(user.id),
                full_name=user.full_name,
                phone=user.phone_number,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            )
        }
    except Exception as e:
        logger.error(f"Login error for user {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/admin/login")
async def admin_login(admin_user: AdminLogin, response: Response = None) -> Any:
    try:
        logger.info(f"Admin login attempt for: {admin_user.email}")
        user = await authenticate_admin_user(admin_user)
        if not user:
            logger.warning(f"Failed admin login attempt for: {admin_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = {
            "user_id": str(user.id),
            "role": user.role,
            "is_active": user.is_active,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=60*60*24*7,  # 7 days
            path="/"
        )
        logger.info(f"Successful admin login for: {user.email}")
        user_response = UserResponse(
            id=str(user.id),
            full_name=user.full_name,
            phone=user.phone_number,
            email=user.email,
            role=user.role,
            is_active=user.is_active
        )
        return {"message": "Login successful", "user": user_response}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error for {admin_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during admin login"
        )

@router.post("/logout")
def logout(request: Request, response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    return {"message": "Logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        phone=current_user.phone_number,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )
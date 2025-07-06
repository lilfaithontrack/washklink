from fastapi import APIRouter
from api.v1.endpoints import auth, users, orders, payments

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User management routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Order management routes
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])

# Payment routes
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, orders, laundry_providers, 
    payments, items, drivers, tracking, realtime
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User management routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Order management routes
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])

# Service provider routes
api_router.include_router(laundry_providers.router, prefix="/laundry-providers", tags=["Laundry Providers"])

# Driver management routes
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])

# Live tracking routes
api_router.include_router(tracking.router, prefix="/tracking", tags=["Live Tracking"])

# Real-time dashboard routes
api_router.include_router(realtime.router, prefix="/realtime", tags=["Real-time Dashboard"])

# Payment routes
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])

# Item management routes
api_router.include_router(items.router, prefix="/items", tags=["Items"])
from fastapi import APIRouter
from api.v1.endpoints import (
    auth,
    users,
    providers,
    items,
    orders,
    payments,
    analytics,
    drivers,
    notifications
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# User management routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Service provider routes
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])

# Items/Services routes
api_router.include_router(items.router, prefix="/items", tags=["items"])

# Order management routes
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])

# Payment routes
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])

# Analytics routes
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Driver management routes
api_router.include_router(drivers.router, prefix="/drivers", tags=["drivers"])

# Notification routes
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
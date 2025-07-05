from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, orders, laundry_providers, payments, items, drivers

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(laundry_providers.router, prefix="/laundry-providers", tags=["Laundry Providers"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(items.router, prefix="/items", tags=["Items"])
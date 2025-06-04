from fastapi import APIRouter
from controllers.booking_controller import booking_router

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

router.include_router(booking_router)

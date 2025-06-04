from fastapi import APIRouter
from controller import booking as booking_controller

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

router.include_router(booking_controller.router)

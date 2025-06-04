from fastapi import APIRouter
from controllers.booking_controller import booking 

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

router.include_router(booking_controller.router)

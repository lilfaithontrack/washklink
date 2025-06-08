from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import booking as models
from schemas import booking as schemas
from typing import List
from sqlalchemy import text

booking_router = APIRouter()
@booking_router.post("/", response_model=schemas.BookingOut)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    total_subtotal = 0
    processed_items = []

    for item in booking.items:
        # IMPORTANT: Ensure your table and column names here EXACTLY match your database
        # Recommend changing 'catagory_id' to 'category_id' in your database for consistency
        item_data = db.execute(
            text("""
                SELECT * FROM tbl_item_price_with_catagory 
                WHERE product_id = :product_id AND catagory_id = :category_id 
            """),
            {"product_id": item.product_id, "category_id": item.category_id}
        ).fetchone()

        if not item_data:
            raise HTTPException(status_code=404, detail=f"Item with product ID {item.product_id} not found")

        # It's good practice to check for out_of_stock, well done.
        if item_data.out_of_stock:
            raise HTTPException(status_code=400, detail=f"Item '{item_data.title}' is out of stock")

        item_subtotal = (item_data.normal_price - item_data.discount) * item.quantity
        total_subtotal += item_subtotal

        # This structure for processed_items is good for storing in the JSON column.
        processed_items.append({
            "product_id": item.product_id,
            "category_id": item.category_id,
            "title": item_data.title,
            "price": item_data.normal_price,
            "quantity": item.quantity,
            "subtotal": item_subtotal
        })

    # --- FIXES APPLIED BELOW ---

    # 1. Calculate delivery charge securely on the backend.
    delivery_charge = booking.delivery_km * 5 if booking.delivery else 0 # Assuming 5 per km

    # 2. Calculate the final total amount on the backend.
    total_amount = total_subtotal + delivery_charge

    # 3. Create the new booking object for the database.
    new_booking = models.Booking(
        user_id=booking.user_id,
        items=processed_items,
        
        # 4. Use the backend-calculated total for the price_tag field.
        #    DO NOT use booking.total_amount.
        price_tag=total_amount, # This field might be redundant if you have subtotal and delivery_charge
        
        subtotal=total_subtotal,
        payment_option=booking.payment_option,
        delivery=booking.delivery,
        delivery_km=booking.delivery_km,
        delivery_charge=delivery_charge,
        cash_on_delivery=booking.cash_on_delivery,
        note=booking.note
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking
@booking_router.get("/", response_model=List[schemas.BookingOut])
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(models.Booking).all()

@booking_router.get("/{booking_id}", response_model=schemas.BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_active_user
from schemas.payment import PaymentInitiate, PaymentCallback, PaymentResponse, PaymentInitiateResponse, PaymentMethod
from services.payment_service import payment_service
from models.users import DBUser
from typing import List

router = APIRouter()

@router.post("/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
    payment_data: PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Initiate payment with selected gateway"""
    try:
        result = await payment_service.initiate_payment(
            db=db,
            order_id=payment_data.order_id,
            payment_method=payment_data.payment_method,
            user=current_user,
            return_url=payment_data.return_url
        )
        
        return PaymentInitiateResponse(
            status=result["status"],
            payment_url=result.get("payment_url"),
            transaction_reference=result["transaction_reference"],
            message=result["message"],
            payment_id=result.get("payment_id")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chapa/callback")
async def chapa_callback(
    callback_data: PaymentCallback,
    db: Session = Depends(get_db)
):
    """Handle Chapa payment callback"""
    try:
        result = await payment_service.handle_callback(
            db=db,
            callback_data=callback_data.dict(),
            payment_method=PaymentMethod.CHAPA
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/telebirr/callback")
async def telebirr_callback(
    callback_data: PaymentCallback,
    db: Session = Depends(get_db)
):
    """Handle Telebirr payment callback"""
    try:
        result = await payment_service.handle_callback(
            db=db,
            callback_data=callback_data.dict(),
            payment_method=PaymentMethod.TELEBIRR
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify/{transaction_id}")
async def verify_payment(
    transaction_id: str,
    payment_method: PaymentMethod,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Verify payment status"""
    try:
        result = await payment_service.verify_payment(
            db=db,
            transaction_id=transaction_id,
            payment_method=payment_method
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_order_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get payment information for an order"""
    payment = payment_service.get_payment_by_order(db, order_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if user has permission to view this payment
    if payment.user_id != current_user.id and not current_user.has_admin_access:
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    
    return payment

@router.get("/my-payments", response_model=List[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get current user's payment history"""
    payments = payment_service.get_user_payments(db, current_user.id)
    return payments

@router.get("/methods")
def get_payment_methods():
    """Get available payment methods"""
    return {
        "methods": [
            {
                "id": "chapa",
                "name": "Chapa",
                "description": "Pay with Chapa - Cards, Mobile Money, Bank Transfer",
                "logo": "https://chapa.co/logo.png",
                "supported_currencies": ["ETB"]
            },
            {
                "id": "telebirr",
                "name": "Telebirr",
                "description": "Pay with Telebirr Mobile Wallet",
                "logo": "https://telebirr.et/logo.png",
                "supported_currencies": ["ETB"]
            },
            {
                "id": "cash_on_delivery",
                "name": "Cash on Delivery",
                "description": "Pay when your order is delivered",
                "logo": None,
                "supported_currencies": ["ETB"]
            }
        ]
    }
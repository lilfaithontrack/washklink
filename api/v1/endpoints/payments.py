from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_current_active_user, get_manager_user
from schemas.payment import PaymentInitiate, PaymentCallback, PaymentResponse, PaymentInitiateResponse, PaymentMethod
from services.payment_service import payment_service
from models.mongo_models import User
from typing import List, Optional
from models.mongo_models import Payment

router = APIRouter(redirect_slashes=False)

@router.post("/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
    payment_data: PaymentInitiate,current_user: User = Depends(get_current_active_user)
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
    callback_data: PaymentCallback):
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
    callback_data: PaymentCallback):
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
    payment_method: PaymentMethod,current_user: User = Depends(get_current_active_user)
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
    order_id: int,current_user: User = Depends(get_current_active_user)
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
def get_my_payments(current_user: User = Depends(get_current_active_user)
):
    """Get current user's payment history"""
    payments = payment_service.get_user_payments(db, current_user.id)
    return payments

@router.get("/methods")
async def get_payment_methods(current_user: User = Depends(get_current_active_user)):
    """Get available payment methods"""
    from models.mongo_models import PaymentMethod
    
    methods = [
        {"id": "chapa", "name": "Chapa", "type": PaymentMethod.CHAPA},
        {"id": "telebirr", "name": "Telebirr", "type": PaymentMethod.TELEBIRR},
        {"id": "cash", "name": "Cash on Delivery", "type": PaymentMethod.CASH_ON_DELIVERY}
    ]
    
    return {"payment_methods": methods}

@router.get("/transactions")
async def get_transactions(
    status: Optional[str] = Query(None, description="Filter by payment status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_manager_user)
):
    """Get payment transactions (Manager/Admin only)"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        payments = await Payment.find(query).skip(skip).limit(limit).sort("-created_at").to_list()
        
        transactions = []
        for payment in payments:
            transactions.append({
                "id": str(payment.id),
                "order_id": str(payment.order_id),
                "user_id": str(payment.user_id),
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.payment_method,
                "status": payment.status,
                "external_transaction_id": payment.external_transaction_id,
                "gateway_reference": payment.gateway_reference,
                "created_at": payment.created_at,
                "completed_at": payment.completed_at
            })
        
        return {"transactions": transactions}
        
    except Exception as e:
        return {"transactions": [], "error": str(e)}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.schemas.payment import PaymentInitiate, PaymentCallback, PaymentResponse
from app.services.payment_gateways.chapa import ChapaPaymentGateway
from app.services.payment_gateways.telebirr import TelebirrPaymentGateway
from app.db.models.user import DBUser

router = APIRouter()

# Initialize payment gateways (you should get these from settings)
chapa_gateway = ChapaPaymentGateway(secret_key="your-chapa-secret-key")
telebirr_gateway = TelebirrPaymentGateway(app_id="your-app-id", app_key="your-app-key")

@router.post("/initiate")
async def initiate_payment(
    payment_data: PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Initiate payment with selected gateway"""
    try:
        if payment_data.payment_method == "chapa":
            result = await chapa_gateway.initiate_payment(
                amount=payment_data.amount,
                order_id=payment_data.order_id,
                return_url=payment_data.return_url
            )
        elif payment_data.payment_method == "telebirr":
            result = await telebirr_gateway.initiate_payment(
                amount=payment_data.amount,
                order_id=payment_data.order_id,
                return_url=payment_data.return_url
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment method")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chapa/callback")
async def chapa_callback(callback_data: PaymentCallback):
    """Handle Chapa payment callback"""
    try:
        result = await chapa_gateway.handle_callback(callback_data.dict())
        # Process the payment result and update your database
        return {"status": "success", "message": "Payment processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/telebirr/callback")
async def telebirr_callback(callback_data: PaymentCallback):
    """Handle Telebirr payment callback"""
    try:
        result = await telebirr_gateway.handle_callback(callback_data.dict())
        # Process the payment result and update your database
        return {"status": "success", "message": "Payment processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify/{transaction_id}")
async def verify_payment(
    transaction_id: str,
    payment_method: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Verify payment status"""
    try:
        if payment_method == "chapa":
            result = await chapa_gateway.verify_payment(transaction_id)
        elif payment_method == "telebirr":
            result = await telebirr_gateway.verify_payment(transaction_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported payment method")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.mongo_models import Payment, PaymentStatus, PaymentMethod
from models.mongo_models import Order
from models.mongo_models import User
from services.payment_gateways.chapa import ChapaPaymentGateway
from services.payment_gateways.telebirr import TelebirrPaymentGateway
from core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class PaymentService:
    def __init__(self):
        # Initialize payment gateways with settings
        self.chapa_gateway = ChapaPaymentGateway(
            secret_key=getattr(settings, 'CHAPA_SECRET_KEY' )
        )
        self.telebirr_gateway = TelebirrPaymentGateway(
            app_id=getattr(settings, 'TELEBIRR_APP_ID', ''),
            app_key=getattr(settings, 'TELEBIRR_APP_KEY', '')
        )

    async def initiate_payment(
        self, 
        db: Session, 
        order_id: int, 
        payment_method: PaymentMethod,
        user: User,
        return_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate payment for an order"""
        
        # Get order details
        order = db.query(Booking).filter(Booking.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if user owns the order or is admin/manager
        if order.user_id != user.id and not user.has_admin_access:
            raise HTTPException(status_code=403, detail="Not authorized to pay for this order")
        
        # Check if order already has a completed payment
        existing_payment = db.query(Payment).filter(
            Payment.order_id == order_id,
            Payment.status == PaymentStatus.COMPLETED
        ).first()
        
        if existing_payment:
            raise HTTPException(status_code=400, detail="Order already paid")

        # Create payment record
        payment = Payment(
            order_id=order_id,
            user_id=user.id,
            amount=order.price_tag,
            payment_method=payment_method,
            status=PaymentStatus.PENDING
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Prepare customer data
        customer_data = {
            "email": user.email or f"user{user.id}@washlink.com",
            "first_name": user.full_name.split()[0] if user.full_name else "Customer",
            "last_name": " ".join(user.full_name.split()[1:]) if len(user.full_name.split()) > 1 else "Name",
            "phone_number": user.phone
        }

        try:
            # Initiate payment with selected gateway
            if payment_method == PaymentMethod.CHAPA:
                result = await self.chapa_gateway.initiate_payment(
                    amount=order.price_tag,
                    order_id=order_id,
                    return_url=return_url,
                    customer_data=customer_data
                )
            elif payment_method == PaymentMethod.TELEBIRR:
                result = await self.telebirr_gateway.initiate_payment(
                    amount=order.price_tag,
                    order_id=order_id,
                    return_url=return_url,
                    customer_data=customer_data
                )
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment method")

            # Update payment with external reference
            if result.get("status") == "success":
                payment.external_transaction_id = result.get("transaction_reference")
                db.commit()
                
                return {
                    "status": "success",
                    "payment_url": result.get("payment_url"),
                    "transaction_reference": result.get("transaction_reference"),
                    "message": result.get("message"),
                    "payment_id": payment.id
                }
            else:
                payment.status = PaymentStatus.FAILED
                db.commit()
                raise HTTPException(status_code=500, detail=result.get("message", "Payment initiation failed"))

        except Exception as e:
            payment.status = PaymentStatus.FAILED
            db.commit()
            logger.error(f"Payment initiation failed for order {order_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_payment(
        self, 
        db: Session, 
        transaction_id: str, 
        payment_method: PaymentMethod
    ) -> Dict[str, Any]:
        """Verify payment status"""
        
        try:
            if payment_method == PaymentMethod.CHAPA:
                result = await self.chapa_gateway.verify_payment(transaction_id)
            elif payment_method == PaymentMethod.TELEBIRR:
                result = await self.telebirr_gateway.verify_payment(transaction_id)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment method")

            # Update payment record if verification successful
            if result.get("status") == "success":
                payment = db.query(Payment).filter(
                    Payment.external_transaction_id == transaction_id
                ).first()
                
                if payment:
                    payment_status = result.get("payment_status", "").lower()
                    if payment_status in ["success", "completed", "paid"]:
                        payment.status = PaymentStatus.COMPLETED
                        payment.gateway_reference = result.get("reference")
                        from datetime import datetime
                        payment.completed_at = datetime.utcnow()
                        
                        # Update order status
                        # Note: This needs to be updated for MongoDB
                        # order = await Order.get(payment.order_id)
                        # if order:
                        #     order.status = OrderStatus.ACCEPTED  # Move to next stage after payment
                        #     await order.save()
                        
                        db.commit()
                        
                        return {
                            "status": "completed",
                            "message": "Payment verified successfully",
                            "amount": result.get("amount"),
                            "reference": result.get("reference")
                        }
                    else:
                        payment.status = PaymentStatus.FAILED
                        db.commit()
                        return {
                            "status": "failed",
                            "message": "Payment verification failed"
                        }
            
            return result

        except Exception as e:
            logger.error(f"Payment verification failed for transaction {transaction_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def handle_callback(
        self, 
        db: Session, 
        callback_data: Dict[str, Any], 
        payment_method: PaymentMethod
    ) -> Dict[str, Any]:
        """Handle payment gateway callback"""
        
        try:
            if payment_method == PaymentMethod.CHAPA:
                result = await self.chapa_gateway.handle_callback(callback_data)
            elif payment_method == PaymentMethod.TELEBIRR:
                result = await self.telebirr_gateway.handle_callback(callback_data)
            else:
                return {"status": "error", "message": "Unsupported payment method"}

            # Find and update payment record
            transaction_id = result.get("transaction_id")
            if transaction_id:
                payment = db.query(Payment).filter(
                    Payment.external_transaction_id == transaction_id
                ).first()
                
                if payment:
                    status = result.get("status", "").lower()
                    if status in ["success", "completed", "paid"]:
                        payment.status = PaymentStatus.COMPLETED
                        payment.gateway_reference = result.get("reference")
                        from datetime import datetime
                        payment.completed_at = datetime.utcnow()
                        
                        # Update order status
                        # Note: This needs to be updated for MongoDB
                        # order = await Order.get(payment.order_id)
                        # if order:
                        #     order.status = OrderStatus.ACCEPTED
                        #     await order.save()
                        
                        db.commit()
                        
                        return {"status": "success", "message": "Payment processed successfully"}
                    else:
                        payment.status = PaymentStatus.FAILED
                        db.commit()
                        return {"status": "failed", "message": "Payment failed"}

            return {"status": "error", "message": "Payment record not found"}

        except Exception as e:
            logger.error(f"Callback processing failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_payment_by_order(self, db: Session, order_id: int) -> Optional[Payment]:
        """Get payment record for an order"""
        return db.query(Payment).filter(Payment.order_id == order_id).first()

    def get_user_payments(self, db: Session, user_id: int) -> list[Payment]:
        """Get all payments for a user"""
        return db.query(Payment).filter(Payment.user_id == user_id).all()

    def get_all_payments(self, db: Session) -> list[Payment]:
        """Get all payments (admin only)"""
        return db.query(Payment).all()

# Global instance
payment_service = PaymentService()
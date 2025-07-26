from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_manager_user
from models.users import DBUser
from crud.user import user_crud
from crud.driver import driver as driver_crud
from services.order_service import get_all_bookings
from sqlalchemy import func
from datetime import datetime, timedelta
from models.booking import OrderStatus
import logging
from db.models.payment import Payment
from schemas.payment import PaymentStatus

logger = logging.getLogger(__name__)

router = APIRouter(redirect_slashes=False)

@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get dashboard statistics (Manager/Admin only)"""
    try:
        # Get user statistics
        total_users = user_crud.get_multi(db)
        regular_users = user_crud.get_regular_users(db)
        admin_users = user_crud.get_admin_users(db)
        
        # Get driver statistics
        all_drivers = driver_crud.get_multi(db)
        available_drivers = driver_crud.get_available_drivers(db)
        
        # Get order statistics
        all_orders = get_all_bookings(db)
        
        # Calculate order stats
        pending_orders = [order for order in all_orders if order.status == OrderStatus.PENDING.value]
        completed_orders = [order for order in all_orders if order.status == OrderStatus.COMPLETED.value]
        in_progress_orders = [order for order in all_orders if order.status in [
            OrderStatus.ASSIGNED.value,
            OrderStatus.ACCEPTED.value,
            OrderStatus.IN_PROGRESS.value,
            OrderStatus.READY_FOR_PICKUP.value,
            OrderStatus.OUT_FOR_DELIVERY.value
        ]]
        cancelled_orders = [order for order in all_orders if order.status == OrderStatus.CANCELLED.value]
        
        # Calculate revenue using real payment data
        completed_payments = db.query(Payment).filter(Payment.status == PaymentStatus.COMPLETED.value).all()
        total_revenue = sum(payment.amount for payment in completed_payments)
        today = datetime.utcnow().date()
        today_completed_payments = [
            payment for payment in completed_payments
            if payment.completed_at and payment.completed_at.date() == today
        ]
        today_revenue = sum(payment.amount for payment in today_completed_payments)
        
        # Calculate today's stats
        today_orders = [
            order for order in all_orders 
            if order.created_at.date() == today
        ]
        today_completed = [
            order for order in today_orders 
            if order.status == OrderStatus.COMPLETED.value
        ]
        today_revenue = sum(order.price_tag for order in today_completed)
        
        stats = {
            "users": {
                "total": len(total_users),
                "regular": len(regular_users),
                "admin": len(admin_users)
            },
            "drivers": {
                "total": len(all_drivers),
                "available": len(available_drivers)
            },
            "orders": {
                "total": len(all_orders),
                "pending": len(pending_orders),
                "in_progress": len(in_progress_orders),
                "completed": len(completed_orders),
                "cancelled": len(cancelled_orders)
            },
            "revenue": {
                "total": total_revenue,
                "today": today_revenue
            },
            "today": {
                "orders": len(today_orders),
                "completed": len(today_completed),
                "revenue": today_revenue
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dashboard statistics: {str(e)}"
        )

@router.get("/users/stats/summary")
def get_user_stats_summary(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get user statistics summary (Manager/Admin only)"""
    try:
        total_users = user_crud.get_multi(db)
        regular_users = user_crud.get_regular_users(db)
        admin_users = user_crud.get_admin_users(db)
        
        return {
            "total_users": len(total_users),
            "regular_users": len(regular_users),
            "admin_users": len(admin_users),
            "active_users": len([user for user in total_users if user.is_active]),
            "inactive_users": len([user for user in total_users if not user.is_active])
        }
    except Exception as e:
        return {
            "total_users": 0,
            "regular_users": 0,
            "admin_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "error": str(e)
        }

@router.get("/orders/stats/summary")
def get_order_stats_summary(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get order statistics summary (Manager/Admin only)"""
    try:
        all_orders = get_all_bookings(db)
        
        return {
            "total_orders": len(all_orders),
            "pending_orders": len([order for order in all_orders if order.status == "pending"]),
            "in_progress_orders": len([order for order in all_orders if order.status == "in_progress"]),
            "completed_orders": len([order for order in all_orders if order.status == "completed"]),
            "cancelled_orders": len([order for order in all_orders if order.status == "cancelled"]),
            "total_revenue": sum([order.total_amount for order in all_orders if order.status == "completed"])
        }
    except Exception as e:
        return {
            "total_orders": 0,
            "pending_orders": 0,
            "in_progress_orders": 0,
            "completed_orders": 0,
            "cancelled_orders": 0,
            "total_revenue": 0,
            "error": str(e)
        } 
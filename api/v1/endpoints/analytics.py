from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_manager_user
from models.mongo_models import User, OrderStatus
from crud.mongo_user import user_mongo_crud
from services.order_service import get_all_orders
from datetime import datetime, timedelta
import logging
from models.mongo_models import Payment
from schemas.payment import PaymentStatus

logger = logging.getLogger(__name__)

router = APIRouter(redirect_slashes=False)

@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_manager_user)):
    """Get dashboard statistics (Manager/Admin only)"""
    try:
        # Get order statistics
        all_orders = await get_all_orders()
        
        # Calculate order stats
        pending_orders = [order for order in all_orders if order.status == OrderStatus.PENDING]
        completed_orders = [order for order in all_orders if order.status == OrderStatus.COMPLETED]
        in_progress_orders = [order for order in all_orders if order.status in [
            OrderStatus.ACCEPTED, OrderStatus.IN_PROGRESS, OrderStatus.OUT_FOR_DELIVERY
        ]]
        
        return {
            "users": {
                "total": 0,  # TODO: Implement user stats
                "regular": 0,
                "admin": 0,
                "active": 0
            },
            "drivers": {
                "total": 0,  # TODO: Implement driver stats
                "available": 0,
                "busy": 0
            },
            "orders": {
                "total": len(all_orders),
                "pending": len(pending_orders),
                "completed": len(completed_orders),
                "in_progress": len(in_progress_orders)
            },
            "revenue": {
                "total": 0,  # TODO: Implement revenue stats
                "today": 0,
                "this_month": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return {
            "users": {"total": 0, "regular": 0, "admin": 0, "active": 0},
            "drivers": {"total": 0, "available": 0, "busy": 0},
            "orders": {"total": 0, "pending": 0, "completed": 0, "in_progress": 0},
            "revenue": {"total": 0, "today": 0, "this_month": 0},
            "error": str(e)
        }

@router.get("/users/stats")
async def get_user_stats_summary(current_user: User = Depends(get_manager_user)):
    """Get user statistics summary (Manager/Admin only)"""
    try:
        # TODO: Implement user statistics with MongoDB
        return {
            "total_users": 0,
            "regular_users": 0,
            "admin_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "note": "User statistics not yet implemented for MongoDB"
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return {
            "total_users": 0,
            "regular_users": 0,
            "admin_users": 0,
            "active_users": 0,
            "inactive_users": 0,
            "error": str(e)
        }

@router.get("/orders/stats/summary")
async def get_order_stats_summary(current_user: User = Depends(get_manager_user)):
    """Get order statistics summary (Manager/Admin only)"""
    try:
        all_orders = await get_all_orders()
        
        return {
            "total_orders": len(all_orders),
            "pending_orders": len([order for order in all_orders if order.status == OrderStatus.PENDING]),
            "in_progress_orders": len([order for order in all_orders if order.status == OrderStatus.IN_PROGRESS]),
            "completed_orders": len([order for order in all_orders if order.status == OrderStatus.COMPLETED]),
            "cancelled_orders": len([order for order in all_orders if order.status == OrderStatus.CANCELLED]),
        }
    except Exception as e:
        logger.error(f"Error getting order stats: {str(e)}")
        return {
            "total_orders": 0,
            "pending_orders": 0,
            "in_progress_orders": 0,
            "completed_orders": 0,
            "cancelled_orders": 0,
            "error": str(e)
        } 

@router.get("/dashboard")
async def get_dashboard_analytics(current_user: User = Depends(get_manager_user)):
    """Get dashboard analytics data (alias for dashboard/stats)"""
    return await get_dashboard_stats(current_user)

@router.get("/revenue")
async def get_revenue_analytics(
    period: str = Query("week", description="Period: day, week, month, year"),
    current_user: User = Depends(get_manager_user)
):
    """Get revenue analytics for specified period"""
    try:
        # TODO: Implement actual revenue calculation from payments
        return {
            "period": period,
            "total_revenue": 0,
            "revenue_data": [],
            "note": "Revenue analytics not yet implemented for MongoDB"
        }
    except Exception as e:
        return {
            "period": period,
            "total_revenue": 0,
            "revenue_data": [],
            "error": str(e)
        }

@router.get("/orders")
async def get_orders_analytics(
    period: str = Query("week", description="Period: day, week, month, year"),
    current_user: User = Depends(get_manager_user)
):
    """Get orders analytics for specified period"""
    try:
        from services.order_service import get_all_orders
        orders = await get_all_orders()
        
        # Basic order statistics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
        pending_orders = len([o for o in orders if o.status == OrderStatus.PENDING])
        
        return {
            "period": period,
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": pending_orders,
            "completion_rate": (completed_orders / total_orders * 100) if total_orders > 0 else 0
        }
    except Exception as e:
        return {
            "period": period,
            "total_orders": 0,
            "completed_orders": 0,
            "pending_orders": 0,
            "completion_rate": 0,
            "error": str(e)
        } 
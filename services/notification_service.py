from typing import List, Optional
from datetime import datetime
from models.mongo_models import Notification
from schemas.notification import NotificationCreate, NotificationType, NotificationCategory
from models.mongo_models import User
from bson import ObjectId

class NotificationService:
    @staticmethod
    async def create_notification(
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        data: Optional[dict] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=ObjectId(user_id),
            title=title,
            message=message,
            type=notification_type,
            data=data
        )
        await notification.insert()
        return notification

    @staticmethod
    async def get_user_notifications(
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = {"user_id": ObjectId(user_id)}
        
        if unread_only:
            query["is_read"] = False
        
        notifications = await Notification.find(query).skip(skip).limit(limit).sort("-created_at").to_list()
        return notifications

    @staticmethod
    async def mark_as_read(notification_id: str, user_id: str) -> Optional[Notification]:
        """Mark a notification as read"""
        try:
            notification = await Notification.find_one({
                "_id": ObjectId(notification_id),
                "user_id": ObjectId(user_id)
            })
            
            if notification and not notification.is_read:
                notification.is_read = True
                await notification.save()
            
            return notification
        except Exception:
            return None

    @staticmethod
    async def mark_all_as_read(user_id: str) -> int:
        """Mark all notifications as read for a user"""
        try:
            result = await Notification.find({"user_id": ObjectId(user_id), "is_read": False}).update_many(
                {"$set": {"is_read": True}}
            )
            return result.modified_count if result else 0
        except Exception:
            return 0

    @staticmethod
    async def delete_notification(notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        try:
            notification = await Notification.find_one({
                "_id": ObjectId(notification_id),
                "user_id": ObjectId(user_id)
            })
            
            if notification:
                await notification.delete()
                return True
            return False
        except Exception:
            return False

    @staticmethod
    async def get_notification_count(user_id: str, unread_only: bool = False) -> int:
        """Get notification count for a user"""
        try:
            query = {"user_id": ObjectId(user_id)}
            if unread_only:
                query["is_read"] = False
            
            count = await Notification.find(query).count()
            return count
        except Exception:
            return 0

    # Helper methods for specific notification types
    @staticmethod
    async def notify_order_status_change(user_id: str, order_id: str, status: str):
        """Create order status change notification"""
        title = "Order Status Update"
        message = f"Your order status has been updated to: {status}"
        data = {"order_id": order_id, "status": status}
        
        return await NotificationService.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="order_update",
            data=data
        )

    @staticmethod
    async def notify_payment_confirmation(user_id: str, payment_id: str, amount: float):
        """Create payment confirmation notification"""
        title = "Payment Confirmed"
        message = f"Your payment of ${amount:.2f} has been confirmed"
        data = {"payment_id": payment_id, "amount": amount}
        
        return await NotificationService.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="payment_confirmation",
            data=data
        )

# Create instance for easier usage
notification_service = NotificationService() 
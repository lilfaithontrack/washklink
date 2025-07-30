from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_current_active_user
from schemas.notification import NotificationResponse, NotificationUpdate
from services.notification_service import notification_service
from models.mongo_models import User

router = APIRouter(redirect_slashes=False)

@router.get("/")
async def get_notifications(
    unread_only: Optional[bool] = Query(False, description="Get only unread notifications"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Get user notifications"""
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=str(current_user.id),
            skip=skip,
            limit=limit,
            unread_only=unread_only
        )
        
        notification_list = []
        for notification in notifications:
            notification_list.append({
                "id": str(notification.id),
                "user_id": str(notification.user_id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "is_read": notification.is_read,
                "data": notification.data,
                "created_at": notification.created_at
            })
        
        return {"notifications": notification_list}
        
    except Exception as e:
        return {"notifications": [], "error": str(e)}

@router.get("/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_active_user)):
    """Get count of unread notifications"""
    try:
        count = await notification_service.get_notification_count(
            user_id=str(current_user.id),
            unread_only=True
        )
        return {"unread_count": count}
    except Exception as e:
        return {"unread_count": 0, "error": str(e)}

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Mark notification as read"""
    try:
        notification = await notification_service.mark_as_read(
            notification_id=notification_id,
            user_id=str(current_user.id)
        )
        
        if notification:
            return {"message": "Notification marked as read", "id": str(notification.id)}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notification: {str(e)}")

@router.put("/mark-all-read")
async def mark_all_notifications_as_read(current_user: User = Depends(get_current_active_user)):
    """Mark all notifications as read"""
    try:
        count = await notification_service.mark_all_as_read(user_id=str(current_user.id))
        return {"message": f"Marked {count} notifications as read", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notifications: {str(e)}")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete notification"""
    try:
        success = await notification_service.delete_notification(
            notification_id=notification_id,
            user_id=str(current_user.id)
        )
        
        if success:
            return {"message": "Notification deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}") 
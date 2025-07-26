from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_manager_user, get_admin_user
from schemas.driver import DriverCreate, DriverUpdate, DriverResponse, DriverStatus, DriverApproval
from crud.driver import driver as driver_crud
from models.users import DBUser
from datetime import datetime
from services.notification_service import notification_service
from db.models.notification import NotificationType, NotificationCategory

router = APIRouter(redirect_slashes=False)

@router.get("/", response_model=List[DriverResponse])
def get_drivers(
    db: Session = Depends(get_db),
    status: DriverStatus = None,
    approval_status: str = None
):
    """Get all drivers (Manager/Admin only)"""
    drivers = driver_crud.get_multi(db)
    
    # Filter by status if provided
    if status:
        drivers = [d for d in drivers if d.status == status]
    
    # Filter by approval status if provided
    if approval_status:
        drivers = [d for d in drivers if d.approval_status == approval_status]
    
    return drivers

@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get driver by ID (Manager/Admin only)"""
    driver = driver_crud.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.post("/", response_model=DriverResponse)
def create_driver(
    driver: DriverCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Create a new driver (Manager/Admin only)"""
    # Convert to dict and set approval_status
    driver_data = driver.dict()
    driver_data['approval_status'] = 'pending'
    driver_data['is_active'] = False
    driver_data['status'] = DriverStatus.OFFLINE
    
    new_driver = driver_crud.create(db, obj_in=driver_data)
    
    # Create notification for admins about new driver
    notification_service.notify_admin_users(
        db=db,
        title="New Driver Registration",
        message=f"New driver {new_driver.first_name} {new_driver.last_name} has registered and needs approval",
        type=NotificationType.INFO,
        category=NotificationCategory.DRIVER,
        reference_id=new_driver.id
    )
    
    return new_driver

@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: int,
    driver: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Update driver information (Manager/Admin only)"""
    existing_driver = driver_crud.get(db, id=driver_id)
    if not existing_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    updated_driver = driver_crud.update(db, db_obj=existing_driver, obj_in=driver)
    
    # Create notification for status changes
    if hasattr(driver, 'status') and driver.status is not None and driver.status != existing_driver.status:
        notification_service.notify_admin_users(
            db=db,
            title="Driver Status Updated",
            message=f"Driver {updated_driver.first_name} {updated_driver.last_name}'s status changed to {driver.status}",
            type=NotificationType.INFO,
            category=NotificationCategory.DRIVER,
            reference_id=driver_id
        )
    
    return updated_driver

@router.post("/{driver_id}/approve", response_model=DriverResponse)
def approve_driver(
    driver_id: int,
    approval: DriverApproval,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_admin_user)
):
    """Approve or reject a driver (Admin only)"""
    driver = driver_crud.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Normalize to lowercase
    driver.approval_status = approval.approval_status.lower()
    driver.approved_by = current_user.id
    driver.approved_at = datetime.utcnow()
    
    if driver.approval_status == "approved":
        driver.is_active = True
        driver.status = DriverStatus.AVAILABLE
        driver.rejection_reason = None
        
        # Create approval notification for admins
        notification_service.notify_admin_users(
            db=db,
            title="Driver Approved",
            message=f"Driver {driver.first_name} {driver.last_name} has been approved",
            type=NotificationType.SUCCESS,
            category=NotificationCategory.DRIVER,
            reference_id=driver.id
        )
    else:
        driver.is_active = False
        driver.status = DriverStatus.SUSPENDED
        driver.rejection_reason = approval.rejection_reason
        
        # Create rejection notification for admins
        notification_service.notify_admin_users(
            db=db,
            title="Driver Rejected",
            message=f"Driver {driver.first_name} {driver.last_name} has been rejected. Reason: {approval.rejection_reason}",
            type=NotificationType.WARNING,
            category=NotificationCategory.DRIVER,
            reference_id=driver.id
        )
    
    db.commit()
    db.refresh(driver)
    return driver

@router.get("/available/list", response_model=List[DriverResponse])
def get_available_drivers(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_manager_user)
):
    """Get all available drivers (Manager/Admin only)"""
    drivers = driver_crud.get_available_drivers(db)
    return drivers 
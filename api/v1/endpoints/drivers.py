from typing import List
from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_manager_user, get_admin_user
from schemas.driver import DriverCreate, DriverUpdate, DriverResponse, DriverStatus, DriverApproval
from models.mongo_models import User, Driver
from datetime import datetime
from services.notification_service import notification_service
from bson import ObjectId

router = APIRouter(redirect_slashes=False)

@router.get("/", response_model=List[DriverResponse])
async def get_drivers(
    status: DriverStatus = None,
    approval_status: str = None,
    current_user: User = Depends(get_manager_user)
):
    """Get all drivers (Manager/Admin only)"""
    try:
        # Build query filters
        query = {}
        if status:
            query["status"] = status
        if approval_status:
            query["is_verified"] = approval_status.lower() == "approved"
        
        # Get drivers from MongoDB
        drivers = await Driver.find(query).to_list()
        
        # Convert to response format
        driver_responses = []
        for driver in drivers:
            driver_responses.append(DriverResponse(
                id=str(driver.id),
                full_name=driver.full_name,
                phone_number=driver.phone_number,
                email=driver.email,
                license_number=driver.license_number,
                vehicle_type=driver.vehicle_type,
                vehicle_plate=driver.vehicle_plate,
                status=driver.status,
                is_verified=driver.is_verified,
                is_available=driver.is_available,
                current_location=driver.current_location,
                rating=driver.rating,
                total_deliveries=driver.total_deliveries
            ))
        
        return driver_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching drivers: {str(e)}")

@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: str,
    current_user: User = Depends(get_manager_user)
):
    """Get driver by ID (Manager/Admin only)"""
    try:
        driver = await Driver.get(ObjectId(driver_id))
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        return DriverResponse(
            id=str(driver.id),
            full_name=driver.full_name,
            phone_number=driver.phone_number,
            email=driver.email,
            license_number=driver.license_number,
            vehicle_type=driver.vehicle_type,
            vehicle_plate=driver.vehicle_plate,
            status=driver.status,
            is_verified=driver.is_verified,
            is_available=driver.is_available,
            current_location=driver.current_location,
            rating=driver.rating,
            total_deliveries=driver.total_deliveries
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching driver: {str(e)}")

@router.post("/", response_model=DriverResponse)
async def create_driver(
    driver: DriverCreate,
    current_user: User = Depends(get_manager_user)
):
    """Create a new driver (Manager/Admin only)"""
    try:
        # Convert to dict and set default values
        driver_data = driver.model_dump()
        driver_data['is_verified'] = False
        driver_data['is_available'] = False
        driver_data['status'] = DriverStatus.OFFLINE
        driver_data['rating'] = 0.0
        driver_data['total_deliveries'] = 0
        
        # Create new driver in MongoDB
        new_driver = Driver(**driver_data)
        await new_driver.insert()
        
        # Create notification for admins about new driver
        await notification_service.create_notification(
            user_id=str(current_user.id),
            title="New Driver Registration",
            message=f"New driver {new_driver.full_name} has registered and needs approval",
            type="INFO",
            category="DRIVER",
            reference_id=str(new_driver.id)
        )
        
        return DriverResponse(
            id=str(new_driver.id),
            full_name=new_driver.full_name,
            phone_number=new_driver.phone_number,
            email=new_driver.email,
            license_number=new_driver.license_number,
            vehicle_type=new_driver.vehicle_type,
            vehicle_plate=new_driver.vehicle_plate,
            status=new_driver.status,
            is_verified=new_driver.is_verified,
            is_available=new_driver.is_available,
            current_location=new_driver.current_location,
            rating=new_driver.rating,
            total_deliveries=new_driver.total_deliveries
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating driver: {str(e)}")

@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: str,
    driver: DriverUpdate,
    current_user: User = Depends(get_manager_user)
):
    """Update driver information (Manager/Admin only)"""
    try:
        # Get existing driver
        existing_driver = await Driver.get(ObjectId(driver_id))
        if not existing_driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Update fields that are provided
        update_data = driver.model_dump(exclude_unset=True)
        old_status = existing_driver.status
        
        for field, value in update_data.items():
            if hasattr(existing_driver, field):
                setattr(existing_driver, field, value)
        
        await existing_driver.save()
        
        # Create notification for status changes
        if 'status' in update_data and update_data['status'] != old_status:
            await notification_service.create_notification(
                user_id=str(current_user.id),
                title="Driver Status Updated",
                message=f"Driver {existing_driver.full_name}'s status changed to {update_data['status']}",
                type="INFO",
                category="DRIVER",
                reference_id=str(driver_id)
            )
        
        return DriverResponse(
            id=str(existing_driver.id),
            full_name=existing_driver.full_name,
            phone_number=existing_driver.phone_number,
            email=existing_driver.email,
            license_number=existing_driver.license_number,
            vehicle_type=existing_driver.vehicle_type,
            vehicle_plate=existing_driver.vehicle_plate,
            status=existing_driver.status,
            is_verified=existing_driver.is_verified,
            is_available=existing_driver.is_available,
            current_location=existing_driver.current_location,
            rating=existing_driver.rating,
            total_deliveries=existing_driver.total_deliveries
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating driver: {str(e)}")

@router.post("/{driver_id}/approve")
async def approve_driver(
    driver_id: str,
    approval: DriverApproval,
    current_user: User = Depends(get_admin_user)
):
    """Approve or reject a driver (Admin only)"""
    try:
        # Get the driver
        driver = await Driver.get(ObjectId(driver_id))
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Update driver verification status
        is_approved = approval.approval_status.lower() == "approved"
        driver.is_verified = is_approved
        
        if not is_approved and approval.rejection_reason:
            # Store rejection reason in driver notes or description field
            driver.notes = f"Rejected: {approval.rejection_reason}"
        
        await driver.save()
        
        action = approval.approval_status.lower()
        return {
            "message": f"Driver {action} successfully",
            "driver_id": str(driver.id),
            "is_verified": driver.is_verified
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating driver approval: {str(e)}")

@router.get("/available/list", response_model=List[DriverResponse])
async def get_available_drivers(
    current_user: User = Depends(get_manager_user)
):
    """Get all available drivers (Manager/Admin only)"""
    try:
        # Get available drivers from MongoDB
        drivers = await Driver.find({
            "is_verified": True,
            "is_available": True,
            "status": DriverStatus.AVAILABLE
        }).to_list()
        
        # Convert to response format
        driver_responses = []
        for driver in drivers:
            driver_responses.append(DriverResponse(
                id=str(driver.id),
                full_name=driver.full_name,
                phone_number=driver.phone_number,
                email=driver.email,
                license_number=driver.license_number,
                vehicle_type=driver.vehicle_type,
                vehicle_plate=driver.vehicle_plate,
                status=driver.status,
                is_verified=driver.is_verified,
                is_available=driver.is_available,
                current_location=driver.current_location,
                rating=driver.rating,
                total_deliveries=driver.total_deliveries
            ))
        
        return driver_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available drivers: {str(e)}") 
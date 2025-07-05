from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.schemas.driver import DriverCreate, DriverResponse, DriverUpdate, LocationUpdate
from app.crud.driver import driver as driver_crud
from app.db.models.user import DBUser
from app.db.models.driver import DriverStatus

router = APIRouter()

@router.get("/", response_model=List[DriverResponse])
def get_all_drivers(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user),
    status: Optional[DriverStatus] = Query(None, description="Filter by driver status"),
    available_only: bool = Query(False, description="Show only available drivers")
):
    """Get all drivers with optional filters"""
    drivers = driver_crud.get_multi(db)
    
    if status:
        drivers = [d for d in drivers if d.status == status]
    
    if available_only:
        drivers = [d for d in drivers if d.status == DriverStatus.AVAILABLE]
    
    return drivers

@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get driver by ID"""
    driver = driver_crud.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.post("/", response_model=DriverResponse)
def create_driver(
    driver: DriverCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Create new driver"""
    # Check for duplicates
    existing_email = driver_crud.get_by_email(db, email=driver.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_phone = driver_crud.get_by_phone(db, phone_number=driver.phone_number)
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    existing_license = driver_crud.get_by_license(db, license_number=driver.license_number)
    if existing_license:
        raise HTTPException(status_code=400, detail="License number already registered")
    
    return driver_crud.create(db, obj_in=driver)

@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: int,
    driver_update: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Update driver information"""
    driver = driver_crud.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return driver_crud.update(db, db_obj=driver, obj_in=driver_update)

@router.put("/{driver_id}/location")
def update_driver_location(
    driver_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Update driver's current location"""
    driver = driver_crud.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    from datetime import datetime
    driver.current_latitude = location.latitude
    driver.current_longitude = location.longitude
    driver.last_location_update = datetime.utcnow()
    driver.last_active = datetime.utcnow()
    
    db.commit()
    return {"message": "Location updated successfully"}

@router.put("/{driver_id}/status")
def update_driver_status(
    driver_id: int,
    status: DriverStatus,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Update driver status"""
    driver = driver_crud.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    driver.status = status
    from datetime import datetime
    driver.last_active = datetime.utcnow()
    
    db.commit()
    return {"message": f"Driver status updated to {status.value}"}

@router.get("/nearby/{latitude}/{longitude}", response_model=List[DriverResponse])
def get_nearby_drivers(
    latitude: float,
    longitude: float,
    radius: float = Query(10.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get drivers within specified radius of given coordinates"""
    from app.services.location_service import location_service
    
    nearby_drivers = location_service.find_nearby_drivers(
        db=db,
        latitude=latitude,
        longitude=longitude,
        max_radius=radius
    )
    
    return [driver for driver, distance in nearby_drivers]
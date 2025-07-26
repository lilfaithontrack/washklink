from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db, get_current_active_user, get_manager_user
from schemas.order import OrderCreate, OrderUpdate, OrderResponse
from models.users import DBUser, UserRole
from services.order_service import (
    create_order_with_items, 
    get_all_orders, 
    get_order_by_id,
    get_orders_by_user
)
from services.assignment_service import assignment_service

router = APIRouter(redirect_slashes=False)

@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Create a new order with automatic provider assignment"""
    if current_user.role == UserRole.USER:
        order.user_id = current_user.id
    elif not order.user_id:
        order.user_id = current_user.id
    return await create_order_with_items(db, order)

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get orders with role-based filtering"""
    if current_user.role == UserRole.USER:
        orders = get_orders_by_user(db, current_user.id)
    else:
        orders = get_all_orders(db)
    return orders

@router.get("/my-orders", response_model=List[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get current user's orders"""
    orders = get_orders_by_user(db, current_user.id)
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_user)
):
    """Get order by ID"""
    order = get_order_by_id(db, order_id)
    if current_user.role == UserRole.USER and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order
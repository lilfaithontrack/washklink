from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_current_active_user, get_manager_user
from schemas.order import OrderCreate, OrderUpdate, OrderResponse
from models.mongo_models import User, UserRole, Order, OrderStatus
from crud.mongo_order import order_mongo_crud
from services.order_service import create_order_with_items
from services.assignment_service import assignment_service

router = APIRouter(redirect_slashes=False)

@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new order with automatic provider assignment"""
    if current_user.role == UserRole.USER:
        order.user_id = str(current_user.id)
    elif not order.user_id:
        order.user_id = str(current_user.id)
    return await create_order_with_items(order)

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get orders with role-based filtering"""
    if current_user.role == UserRole.USER:
        orders = await order_mongo_crud.get_by_user(str(current_user.id), skip=skip, limit=limit)
    else:
        orders = await order_mongo_crud.get_multi(skip=skip, limit=limit)
    
    return [OrderResponse(
        id=str(order.id),
        user_id=str(order.user_id),
        service_provider_id=str(order.service_provider_id) if order.service_provider_id else None,
        driver_id=str(order.driver_id) if order.driver_id else None,
        status=order.status,
        service_type=order.service_type,
        subtotal=order.subtotal,
        delivery=order.delivery,
        delivery_charge=order.delivery_charge,
        pickup_address=order.pickup_address,
        delivery_address=order.delivery_address,
        created_at=order.created_at,
        items=order.items
    ) for order in orders]

@router.get("/my-orders", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get current user's orders"""
    orders = await order_mongo_crud.get_by_user(str(current_user.id), skip=skip, limit=limit)
    return [OrderResponse(
        id=str(order.id),
        user_id=str(order.user_id),
        service_provider_id=str(order.service_provider_id) if order.service_provider_id else None,
        driver_id=str(order.driver_id) if order.driver_id else None,
        status=order.status,
        service_type=order.service_type,
        subtotal=order.subtotal,
        delivery=order.delivery,
        delivery_charge=order.delivery_charge,
        pickup_address=order.pickup_address,
        delivery_address=order.delivery_address,
        created_at=order.created_at,
        items=order.items
    ) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get order by ID"""
    order = await order_mongo_crud.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.role == UserRole.USER and str(order.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return OrderResponse(
        id=str(order.id),
        user_id=str(order.user_id),
        service_provider_id=str(order.service_provider_id) if order.service_provider_id else None,
        driver_id=str(order.driver_id) if order.driver_id else None,
        status=order.status,
        service_type=order.service_type,
        subtotal=order.subtotal,
        delivery=order.delivery,
        delivery_charge=order.delivery_charge,
        pickup_address=order.pickup_address,
        delivery_address=order.delivery_address,
        created_at=order.created_at,
        items=order.items
    )

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update order details"""
    order = await order_mongo_crud.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only allow users to update their own orders or managers/admins to update any order
    if current_user.role == UserRole.USER and str(order.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this order")
    
    updated_order = await order_mongo_crud.update(order_id, order_update)
    if not updated_order:
        raise HTTPException(status_code=400, detail="Failed to update order")
    
    return OrderResponse(
        id=str(updated_order.id),
        user_id=str(updated_order.user_id),
        service_provider_id=str(updated_order.service_provider_id) if updated_order.service_provider_id else None,
        driver_id=str(updated_order.driver_id) if updated_order.driver_id else None,
        status=updated_order.status,
        service_type=updated_order.service_type,
        subtotal=updated_order.subtotal,
        delivery=updated_order.delivery,
        delivery_charge=updated_order.delivery_charge,
        pickup_address=updated_order.pickup_address,
        delivery_address=updated_order.delivery_address,
        created_at=updated_order.created_at,
        items=updated_order.items
    )

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: dict,
    current_user: User = Depends(get_manager_user)
):
    """Update order status (Manager/Admin only)"""
    try:
        order = await order_mongo_crud.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        new_status = OrderStatus(status_data.get("status"))
        order.status = new_status
        await order.save()
        
        return {
            "message": "Order status updated successfully",
            "order_id": str(order.id),
            "status": order.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating order status: {str(e)}")

@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete order"""
    order = await order_mongo_crud.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only allow users to delete their own pending orders or managers/admins to delete any order
    if current_user.role == UserRole.USER:
        if str(order.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this order")
        if order.status != OrderStatus.PENDING:
            raise HTTPException(status_code=400, detail="Can only delete pending orders")
    
    success = await order_mongo_crud.delete(order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete order")
    
    return {"message": "Order deleted successfully"}
from typing import Annotated

from fastapi import APIRouter, Depends, Query,status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import order_service

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Order:
    """Crea un nuevo pedido para el usuario autenticado"""
    return await order_service.create_order(
        db, order_in=order_in, current_user_id=current_user.id
    )


@router.get("/", response_model=list[OrderResponse])
async def read_my_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[Order]:
    """Obtiene el historial de pedidos del usuario autenticado"""
    return await order_service.get_user_orders(
        db, current_user_id=current_user.id, skip=skip, limit=limit
    )


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Order:
    """Actualiza el estado o monto de un pedido propio"""
    return await order_service.update_user_order(
        db, order_id=order_id, order_in=order_in, current_user_id=current_user.id
    )


@router.delete("/{order_id}", response_model=OrderResponse)
async def delete_order(
    order_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Order:
    """Elimina un pedido propio"""
    return await order_service.delete_user_order(
        db, order_id=order_id, current_user_id=current_user.id
    )
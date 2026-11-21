from datetime import datetime, timezone
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.order import Order, OrderStatus
from app.repositories.order_repository import order_repo
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    def _generate_order_code(self) -> str:
        """Genera un código único de negocio: ORD-YYYYMMDD-HEX6"""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        random_hex = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_str}-{random_hex}"

    async def create_order(
        self, db: AsyncSession, *, order_in: OrderCreate, current_user_id: int
    ) -> Order:
        for _ in range(3):
            # 1. El Backend genera el código único automáticamente
            order_code = self._generate_order_code()
            try:
                # 2. Crear la orden asociada al usuario autenticado
                return await order_repo.create_for_user(
                    db,
                    obj_in=order_in,
                    user_id=current_user_id,
                    order_code=order_code,
                )
            except IntegrityError:
                await db.rollback()
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo generar el codigo de pago unico, intenta de nuevo"
        )
    async def get_user_orders(
        self,
        db: AsyncSession,
        *,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        return await order_repo.get_multi_by_user(
            db, user_id=current_user_id, skip=skip, limit=limit
        )

    async def update_user_order(
        self,
        db: AsyncSession,
        *,
        order_id: int,
        order_in: OrderUpdate,
        current_user_id: int,
    ) -> Order:
        order = await order_repo.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )
        if order.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar este pedido",
            )
        if order.status in (OrderStatus.PAID , OrderStatus.CANCELLED):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = f"No se puede modificar un pedido en estado {order.status}" 
            )
        return await order_repo.update(db, db_obj=order, obj_in=order_in)

    async def delete_user_order(
        self, db: AsyncSession, *, order_id: int, current_user_id: int
    ) -> Order:
        order = await order_repo.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido no encontrado",
            )
        if order.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar este pedido",
            )
        if order.status  == OrderStatus.PAID:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "No se puede eliminar un pedido que ya ha sido pagado"
            )
        return await order_repo.delete_order(db, db_obj=order) 


order_service = OrderService()
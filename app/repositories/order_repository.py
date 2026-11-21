from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.repositories.base import RepositoryBase
from app.schemas.order import OrderCreate, OrderUpdate


class RepositoryOrder(RepositoryBase[Order, OrderCreate, OrderUpdate]):
    async def get_by_code(
        self, db: AsyncSession, *, order_code: str
    ) -> Order | None:
        """Busca una orden por su codigo unico"""
        stmt = select(Order).where(Order.order_code == order_code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Order]:
        """Obtiene todas las ordenes de un usuario especifico ordenadas por las mas reciente"""
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc(), Order.id.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: OrderCreate, user_id: int, order_code:str
    ) -> Order:
        """Crea un pedido con el codigo autogenerado y el usuario autenticado"""
        db_obj = Order(**obj_in.model_dump(), user_id=user_id, order_code=order_code)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete_order(self, db: AsyncSession, *, db_obj: Order) -> Order:
        """ Elimina una orden ya cargada en sesion sin hacer soble consulta """
        await db.delete(db_obj)
        await db.commit()
        return db_obj

# Exportamos la instancia
order_repo = RepositoryOrder(Order)
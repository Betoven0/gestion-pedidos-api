from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

# Aqui definimos varibles de tipo (Typevar) para que python sepa que estamos manejando
ModelType = TypeVar("ModelType", bound=Base)  # Modelo SQLAlchemy
CreateShemaType = TypeVar("CreateShemaType", bound=BaseModel)  # Esquema Pydantic Create
UpdateShemaType = TypeVar("UpdateShemaType", bound=BaseModel)  # Esquema Pydantic Update


class RepositoryBase(Generic[ModelType, CreateShemaType, UpdateShemaType]):
    def __init__(self, model: type[ModelType]):
        """
        El repositorio recibe el modelo de SQLAlchemy sobre el que va a operar
        EJ: RepositoryBase(User)
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """
        Obtiene multiples registros con paginacion
        """
        return await db.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Obtiene multiples registros con paginacion"""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateShemaType) -> ModelType:
        """Crea un nuevo registro en la base de datos"""
        # Se convierte el esquiema de Pyndantic a un diccionario
        obj_in_data = obj_in.model_dump()

        # Se inicia el modelo de SQLAlchemy
        db_obj = self.model(**obj_in_data)

        # Lo agregamos a la sesion y hacemos commit a la base de datos
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateShemaType | dict[str, Any],
    ) -> ModelType:
        """Actualiza un registro existente"""
        obj_data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        # Actualizamos los atributos que hayan cambiado
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> ModelType | None:
        """Elimina un registro de la base de datos"""
        obj = await db.get(self.model, id)
        if not obj:
            return None
        await db.delete(obj)
        await db.commit()
        return obj

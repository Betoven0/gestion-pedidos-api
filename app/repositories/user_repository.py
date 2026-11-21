from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import RepositoryBase
from app.schemas.user import UserCreate, UserUpdate


class RepositoryUser(RepositoryBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """Busca un usuario por su correo electronico"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_with_hash(
        self, db: AsyncSession, *, obj_in: UserCreate, hashed_password: str
    ) -> User:
        """Crea un usuario guardando el hash de la contraseña en vez del texto plano"""
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


# Exportamos una instancia lista para ser usada por los  servicios
user_repo = RepositoryUser(User)

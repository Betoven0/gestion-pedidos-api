import asyncio

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    DUMMY_PASSWORD_HASH,
    get_password_hash, 
    verify_password
    )
from app.models.user import User
from app.repositories.user_repository import user_repo
from app.schemas.user import UserCreate


class UserService:
    async def register_user(self, db: AsyncSession, *, user_in: UserCreate) -> User:

        # 1 Regla de negocio: el email no puede repetirse
        existing_user = await user_repo.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electronico ya esta registrado",
            )

        # 2 Seguridad: Hashear en un proceso separado para no congelar el servidor

        hashed_pwd = await asyncio.to_thread(get_password_hash, user_in.password)

        # 3 Guardar en la base de datos usando el repositorio protegiendo contra el doble click
        try:
            return await user_repo.create_with_hash(
                db, obj_in= user_in, hashed_password=hashed_pwd
            )
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST,
                detail="El correo electronico ya esta registrado"
            )


    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> User | None:
        normalize_email = email.lower().strip()
        user = await user_repo.get_by_email(db, email=normalize_email)
        if not user:
            #Mandamos a llamar a bcrypt  contra el hash señuelo para evitar Timing Attacks
            await asyncio.to_thread(verify_password, password, DUMMY_PASSWORD_HASH)
            return None
        is_valid= await asyncio.to_thread(
            verify_password, password, user.hashed_password
        )
        if not is_valid:
            return None
        if not user.is_active:
            return None
        return user


user_service = UserService()

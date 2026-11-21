from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import user_repo
from app.schemas.token import TokenPayload

# esto le indica a FastAPI y a swagger ui donde esta el endpoint de login
# Habilita el boton verde "Authorize" en la documentacion automatica

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(reusable_oauth2)],
) -> User:
    """
    Dependencia que extrae el token JWT del Header 'Authorization: Bearer <token>',
    lo decodifica, verifica su vigencia y busca al usuario en la base de datos
    """
    try:
        # Decodificamos el token usuando nuestra clave secreta y algoritmo
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Validamos que el paylload tenga la estructura correcta con Pydantic
        token_data = TokenPayload(**payload)

        if token_data.sub is None:
            raise jwt.InvalidTokenError("El token no contiene el identificador 'sub'")
        user_id = int(token_data.sub)

    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        ValidationError,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Las credenciales no son validas o el token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Buscamos al usuario en la base de datos usando el repositorio
    user = await user_repo.get(db, id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN, detail= "User Inactive"
        )

    return user

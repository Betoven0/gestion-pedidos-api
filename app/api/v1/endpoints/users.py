from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import user_service

router = APIRouter()

@router.post("/", response_model=UserResponse,
status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Registra un nuevo usuario en el sistema"""
    return await user_service.register_user(db, user_in=user_in)

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Devuelve la informacion del usuario actualmente autenticado"""
    return current_user
    
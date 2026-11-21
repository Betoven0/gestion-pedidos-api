from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

#Solo pasamod check_same_thread si el motor es sqlite
connect_args =(
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else{}
)


#Motor de base de datos
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False, #Cambia a true si quieres ver las consultas sql en la terminal
    connect_args=connect_args
)

#Generador de Sesiones
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

#inyector de dependencias para endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
from pathlib import Path
from typing import Annotated

from fastapi import Depends ,FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import get_db

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Página principal (Frontend Dashboard)
@app.get("/", include_in_schema=False)
async def serve_spa() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# prueba de salud del servidor y base de datos
@app.get("/health", tags=["Sistema"])
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected", "environment": "WSL2 Ubuntu"}


# Aqui conectamos todos los endpoints reales de la aplicacion
app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi import APIRouter

from app.api.v1.endpoints import auth, orders,users

api_router = APIRouter()

# Conectamos cada módulo de endpoints y les asignamos un prefijo y una etiqueta para Swagger UI
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(orders.router, prefix="/orders", tags=["Órdenes"])

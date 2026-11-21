from collections.abc import AsyncGenerator

from httpx import ASGITransport ,AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app

#1 Motor de base de datos en RAM exclusivo para pruebas

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(
    bind= test_engine,
    class_= AsyncSession,
    expire_on_commit=False
)

#2 Reemplazo de get_db para que los endpoinsts usen la Base de datos de la Memoria RAM
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

#3 Fixtrue: antes de cada text crea las tablas limpias, y al terminas se borran de la base de datos
@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

#PRUEBAS AUTOMATICAS DE LA API(tEST)

@pytest.mark.asyncio
async def  test_health_check():
    """Verifica que el servidor responda correctamente en /health y sirva el frontend Stitch en /"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["database"] == "connected"

        frontend_res = await client.get("/")
        assert frontend_res.status_code == 200
        assert "text/html" in frontend_res.headers["content-type"]
        assert "Panel de Gestión de Pedidos" in frontend_res.text
        assert "view-playground" in frontend_res.text

@pytest.mark.asyncio
async def test_full_user_and_order_flow():
    """
    Prueba de integración completa:
    1. Registrar usuario (201)
    2. Iniciar sesión y obtener JWT (200)
    3. Crear un pedido y verificar que el Backend autogenere el order_code (201)
    4. Listar los pedidos del usuario (200)
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        #1Registra al usuario
        reg_res = await client.post(
            "api/v1/users/",
            json={
                "email": "junior@ejemplo.com",
                "full_name": "Diego Dev",
                "password": "passwordSeguro123"
            }
        )
        assert reg_res.status_code == 201
        assert reg_res.json()["email"] == "junior@ejemplo.com"

        #2 Login OAuth2 para obtener el JWT
        login_res = await client.post(
            "api/v1/auth/login",
            data={
                "username": "junior@ejemplo.com",
                "password": "passwordSeguro123"
            }
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        #3Crear un pedido autenticado (Sin enviar order_code)
        order_res = await client.post(
            "api/v1/orders/",
            json={"total_amount": 250.50, "status": "PENDING"},
            headers=headers
        )
        assert order_res.status_code == 201
        order_data = order_res.json()
        assert order_data["total_amount"] == 250.50
        assert order_data["order_code"].startswith("ORD-")

        #4 consultar mis pedidos
        list_res = await client.get("/api/v1/orders/", headers=headers)
        assert list_res.status_code ==200
        assert len(list_res.json()) == 1


@pytest.mark.asyncio
async def test_unauthorized_order_access():
    """Verifica que  no se puedan crear pedidos sin token JWT(401)"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "api/v1/orders/",
            json={"total_amount": 100.00, "status": "PENDING"}
        ) 
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_order_business_rules_and_security():
    """
    Verifica las reglas de producción:
    1. No permitir correos duplicados aunque usen mayúsculas (400)
    2. No permitir editar ni borrar un pedido ya pagado PAID (400)
    3. No permitir que otro usuario modifique o borre un pedido ajeno (403)
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Registrar Usuario A
        await client.post(
            "/api/v1/users/",
            json={
                "email": "cliente@ejemplo.com",
                "full_name": "Cliente Uno",
                "password": "passwordSeguro123",
            },
        )

        # Intentar registrar el mismo correo con MAYÚSCULAS -> Debe fallar con 400
        dup_res = await client.post(
            "/api/v1/users/",
            json={
                "email": "CLIENTE@ejemplo.com",
                "full_name": "Clon",
                "password": "passwordSeguro123",
            },
        )
        assert dup_res.status_code == 400

        # Login Usuario A
        login_a = await client.post(
            "/api/v1/auth/login",
            data={"username": "cliente@ejemplo.com", "password": "passwordSeguro123"},
        )
        headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

        # Crear pedido en PENDING
        order_res = await client.post(
            "/api/v1/orders/",
            json={"total_amount": 150.00, "status": "PENDING"},
            headers=headers_a,
        )
        order_id = order_res.json()["id"]

        # 2. Registrar y loguear Usuario B (Intruso)
        await client.post(
            "/api/v1/users/",
            json={
                "email": "intruso@ejemplo.com",
                "full_name": "Intruso",
                "password": "passwordSeguro123",
            },
        )
        login_b = await client.post(
            "/api/v1/auth/login",
            data={"username": "intruso@ejemplo.com", "password": "passwordSeguro123"},
        )
        headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

        # Usuario B intenta modificar el pedido del Usuario A -> Debe dar 403 Forbidden
        idor_res = await client.patch(
            f"/api/v1/orders/{order_id}",
            json={"status": "CANCELLED"},
            headers=headers_b,
        )
        assert idor_res.status_code == 403

        # 3. Usuario A paga su pedido (pasa de PENDING a PAID) -> 200 OK
        pay_res = await client.patch(
            f"/api/v1/orders/{order_id}",
            json={"status": "PAID"},
            headers=headers_a,
        )
        assert pay_res.status_code == 200

        # Intentar cambiar el monto de un pedido ya PAID -> Debe dar 400 Bad Request
        tamper_res = await client.patch(
            f"/api/v1/orders/{order_id}",
            json={"total_amount": 1.00},
            headers=headers_a,
        )
        assert tamper_res.status_code == 400

        # Intentar eliminar un pedido ya PAID -> Debe dar 400 Bad Request
        del_paid_res = await client.delete(
            f"/api/v1/orders/{order_id}",
            headers=headers_a,
        )
        assert del_paid_res.status_code == 400
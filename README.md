# 📦 Gestión de Pedidos API

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Async_REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_Async-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-4%2F4_Passing-10B981?style=flat-square&logo=pytest&logoColor=white)

Sistema de gestión de pedidos con una **API REST asíncrona en FastAPI** y una **Consola Web Interactiva** diseñada con Google Stitch para registrar usuarios, administrar órdenes en tiempo real y probar los endpoints desde el navegador.

---

## ✨ ¿Qué incluye este proyecto?

En lugar de ser solo un backend sin interfaz, la aplicación integra **el motor de negocio** y un **portal visual interactivo** en un solo lugar:

| Módulo Visual | ¿Para qué sirve? |
| :--- | :--- |
| 🛍️ **Mis Pedidos & Sesión** | Panel principal para crear una cuenta, iniciar sesión, generar nuevos pedidos y cambiar su estado (**Pagar**, **Cancelar** o **Eliminar**) viendo estadísticas en vivo. |
| 📊 **Overview & Quickstart** | Resumen del estado del servidor conectado en tiempo real a la base de datos y guía rápida con ejemplos listos para copiar en `cURL`, `JavaScript` y `Python`. |
| ⚡ **API Playground** | Un *Postman integrado en la página*: permite enviar peticiones reales al servidor, medir cuántos milisegundos tarda en responder y ver el JSON en vivo. |
| 📖 **Endpoint Reference** | Catálogo interactivo con las rutas disponibles de la API, sus ejemplos de respuesta y acceso directo para probarlas en el Playground. |

---

## 🛡️ Buenas Prácticas de Ingeniería Aplicadas

Detrás de una interfaz sencilla, el backend está construido cuidando los detalles que importan en un entorno real:

* 💰 **Dinero Exacto (`Decimal`):** Los montos utilizan precisión decimal exacta (`Numeric(10, 2)`) en lugar de decimales aproximados (`float`), evitando descuadres de centavos.
* 🔄 **Flujo Lógico de Estados:** Todo pedido nuevo nace siempre como **Pendiente (`PENDING`)**. Una vez que un pedido se marca como **Pagado (`PAID`)**, queda protegido: no se le puede alterar el precio ni puede ser eliminado por accidente.
* 🏷️ **Códigos Únicos Automáticos:** El servidor genera automáticamente folios únicos con formato `ORD-YYYYMMDD-XXXXXX` y reintenta automáticamente si llegara a ocurrir una colisión.
* 🔒 **Seguridad y Rendimiento:**
  * Contraseñas encriptadas con `bcrypt` en segundo plano (`asyncio.to_thread`) para que el servidor nunca se congele.
  * Sesiones protegidas con tokens **JWT** donde cada usuario solo puede ver y modificar sus propios pedidos.
  * Correos normalizados automáticamente a minúsculas para evitar cuentas duplicadas.

---

## 🗂️ Estructura del Proyecto

El código está organizado por capas para que cada archivo tenga una responsabilidad clara:

```text
gestion-pedidos-api/
├── app/
│   ├── api/v1/          # Rutas HTTP (/auth, /users, /orders) y validación de token JWT
│   ├── core/            # Configuración general y seguridad (Bcrypt + JWT)
│   ├── db/              # Conexión asíncrona a base de datos (SQLite / PostgreSQL)
│   ├── models/          # Tablas de la base de datos (User y Order)
│   ├── repositories/    # Consultas limpias a la base de datos
│   ├── schemas/         # Validación de datos de entrada y salida (Pydantic v2)
│   ├── services/        # Reglas de negocio (creación de folios, estados y permisos)
│   ├── static/          # Interfaz web interactiva (index.html)
│   └── main.py          # Punto de arranque de la aplicación
└── tests/
    └── test_api.py      # Pruebas automáticas de principio a fin (Pytest)
```

---

## 🚀 Cómo probarlo en tu computadora (3 pasos)

### 1. Preparar el entorno e instalar librerías
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd gestion-pedidos-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Crear las tablas de la base de datos
```bash
cp .env.example .env
python -m app.db.init_db
```

### 3. Encender el servidor
```bash
uvicorn app.main:app --reload
```

Abre en tu navegador:
* 🖥️ **Consola Web Interactiva:** [http://localhost:8000](http://localhost:8000)
* 📄 **Documentación Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Ejecutar las pruebas automáticas

Para comprobar que el registro, el login, la creación de pedidos y todas las reglas de seguridad funcionan correctamente:

```bash
python -m pytest -v
```

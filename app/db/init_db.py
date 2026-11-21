import asyncio
from app.db.session import engine
from app.db.base import Base

#IMPORTANTE debemos importar los modelos despues de la clase de "Base"
# para que asi se entere de que existen antes de crear tablas

from app.models.user import User
from app.models.order import Order

async def init_models():
    """
    Se conecta al motor de base de datos asincrono y ordena crear
    todas las tablas definidas que hereden de "Base"
    """
    print("Iniciando la creacion de tablas de la base de datos")

    async with engine.begin() as conn:
        #Crea las tablas si no existen
        await conn.run_sync(Base.metadata.create_all)
    print("Todas las tablas creadas con exito! Revisa tu explorador d archivos.")

if __name__ == "__main__":
    #Como es una funcion asyncrona, necesitamos el event loop de asyncio para correrla
    asyncio.run(init_models())
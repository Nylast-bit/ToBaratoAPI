from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Usa el driver asyncpg en la URL
URL_DATABASE = "postgresql+asyncpg://postgres:tzAo3bevuc9kU6F6kY651qcnyqGXuQEn0DbYNtGNjX37zLPeH4AdauGmYqVG5OSK@190.166.156.93:5432/postgres"

if not URL_DATABASE:
    raise ValueError("La URL de la base de datos no está configurada")

# ✅ Motor asincrónico
engine = create_async_engine(URL_DATABASE, echo=True)

# ✅ Sesión asincrónica
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

# Base declarativa
Base = declarative_base()

# Función para inicializar la base de datos
async def init_db():
    async with engine.begin() as conn:
        # Crear todas las tablas en la base de datos
        await conn.run_sync(
            lambda conn: Base.metadata.create_all(
                bind=conn,
                tables=None,  # Todas las tablas
                checkfirst=True  # Verificar primero si existen
            )
)


# Example of how to use it in your main application
async def main():
    await init_db()
    print("Database initialized!")

if __name__ == "__main__":
    asyncio.run(main())
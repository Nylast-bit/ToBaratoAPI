from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()  # Cargar las variables del .env

# 🚀 Intenta primero leer DATABASE_URL completa del entorno (ideal en producción)
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no existe DATABASE_URL completa, construirla desde variables individuales (útil en desarrollo)
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "10.0.0.80")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")

    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Validación explícita
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada correctamente.")

# Crear el motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear la sesión
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

# Declaración base para los modelos
Base = declarative_base()

# Inicialización de la base de datos
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Ejecutar de forma independiente (por ejemplo, para pruebas)
if __name__ == "__main__":
    asyncio.run(init_db())
    print("✅ Base de datos inicializada correctamente.")

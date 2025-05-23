from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
from dotenv import load_dotenv
import asyncio


load_dotenv()

# Usa el driver estándar de SQLAlchemy en la URL
URL_DATABASE = "postgresql://postgres:tzAo3bevuc9kU6F6kY651qcnyqGXuQEn0DbYNtGNjX37zLPeH4AdauGmYqVG5OSK@190.166.156.93:5432/postgres"

if not URL_DATABASE:
    raise ValueError("La URL de la base de datos no está configurada")

# ✅ Motor Síncrono (para Alembic)
engine = create_engine(URL_DATABASE, echo=True)

# ✅ Sesión Síncrona (para Alembic)
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=Session,  # Usamos la clase de Session sincrónica
    autoflush=False,
    autocommit=False,
)

# Base declarativa
Base = declarative_base()

# Función para inicializar la base de datos
def init_db():
    with engine.begin() as conn:
        # Crear todas las tablas en la base de datos
        Base.metadata.create_all(bind=conn, checkfirst=True)

# Ejemplo de cómo usarlo en tu aplicación principal
if __name__ == "__main__":
    init_db()
    print("Database initialized!")

import os
import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- Configuración crítica de paths ---
# Añade el directorio raíz del proyecto al PYTHONPATH
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, project_root)

# --- Importación de modelos ---
# Importa después de configurar el path
from app.models.models import Base  # Asegúrate que esta ruta sea correcta
from app.database import engine  # Importa tu engine configurado

# --- Configuración de Alembic ---
config = context.config
target_metadata = Base.metadata

# Configuración de logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# --- Funciones de migración ---
def run_migrations_offline():
    """Ejecuta migraciones en modo offline (sin conexión a BD)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecuta migraciones en modo online (con conexión a BD)."""
    # Usa el engine directamente en lugar de engine_from_config
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()

# --- Ejecución principal ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
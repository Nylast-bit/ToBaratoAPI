import sys
from pathlib import Path
from sqlalchemy import text  # Importa text para ejecutar SQL directo

# Añade el directorio raíz al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from app.models.models import Base
from app.database import engine

def reset_database():
    print("⚠️ ¡ADVERTENCIA! Esto borrará TODOS los datos de la BD.")
    confirmacion = input("¿Estás seguro? (escribe 'SI' para continuar): ")
    
    if confirmacion.strip().upper() == "SI":
        print("Eliminando tablas...")
        
        # Conexión para PostgreSQL - usando text()
        with engine.begin() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        
        print("Creando tablas nuevas...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ ¡Base de datos reiniciada exitosamente!")
    else:
        print("❌ Operación cancelada.")

if __name__ == "__main__":
    reset_database()
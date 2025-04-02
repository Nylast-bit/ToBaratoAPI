from app.main import app  # Importa la aplicación correctamente
from app.database import engine
from app.models.models import Base

# Crea todas las tablas definidas en los modelos
Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

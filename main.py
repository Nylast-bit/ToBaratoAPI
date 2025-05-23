from app.main import app
from app.database import engine
from app.models.models import Base
import asyncio

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    # Crear tablas antes de iniciar la aplicación
    asyncio.run(create_tables())
    
    # Iniciar servidor Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=True)
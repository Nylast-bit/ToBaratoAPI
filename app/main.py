from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from app.database import engine, Base, init_db
from app.routes import tipoproveedor, tipousuario, categoria, unidadmedida, usuario, lista, producto, proveedor, listaproductos, usuarioproveedor, productoproveedor, sucursal, dashboard

app = FastAPI(title="To-Barato API")

# 👇 Esto es nuevo también
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O usa ["*"] si solo estás desarrollando
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra los routers
app.include_router(tipoproveedor.router, prefix="/api")
app.include_router(tipousuario.router, prefix="/api")
app.include_router(categoria.router, prefix="/api")
app.include_router(unidadmedida.router, prefix="/api")
app.include_router(usuario.router, prefix="/api")
app.include_router(lista.router, prefix="/api")
app.include_router(producto.router, prefix="/api")
app.include_router(proveedor.router, prefix="/api")
app.include_router(sucursal.router, prefix="/api")
app.include_router(listaproductos.router, prefix="/api")
app.include_router(usuarioproveedor.router, prefix="/api")
app.include_router(productoproveedor.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.on_event("startup")
async def startup():
    # Llamamos a la función de inicialización para crear las tablas en la base de datos
    await init_db()

@app.get("/")
def root():
    return {"message": "¡API viva!"}

@app.get("/health")
async def health_check():
    """Endpoint simple para healthcheck del contenedor Docker"""
    return {"status": "ok"}

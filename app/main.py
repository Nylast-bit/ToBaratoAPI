from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 Esto es nuevo
from app.database import engine, Base
from app.routes import tipoproveedor, tipousuario, categoria, unidadmedida, usuario, lista, producto, proveedor, listaproductos, usuarioproveedor, productoproveedor, sucursal

app = FastAPI(title="To-Barato API")

# 👇 Esto es nuevo también
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O usa ["*"] si solo estás desarrollando
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas (solo desarrollo)
Base.metadata.create_all(bind=engine)

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


@app.get("/")
def root():
    return {"message": "¡API viva!"}

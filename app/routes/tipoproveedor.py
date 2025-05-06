from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from app.models.models import TipoProveedor
from app.database import AsyncSessionLocal  # Usar AsyncSessionLocal
from app.schemas.tipoproveedor import TipoProveedorCreate, TipoProveedorResponse

router = APIRouter()

# Dependencia para obtener la sesión de base de datos asincrónica
async def get_db():
    db = AsyncSessionLocal()  # Usar AsyncSessionLocal para obtener la sesión asincrónica
    try:
        yield db
    finally:
        await db.close()  # Cerrar la sesión de forma asincrónica

db_dependency = Annotated[AsyncSession, Depends(get_db)]  # Usar AsyncSession aquí

# Crear un nuevo tipo de proveedor
@router.post("/tipoproveedor", response_model=TipoProveedorResponse)
async def crear_tipo_proveedor(tipoProveedorParam: TipoProveedorCreate, db: AsyncSession = Depends(get_db)):
    nuevo_tipo = TipoProveedor(
        NombreTipoProveedor=tipoProveedorParam.NombreTipoProveedor
    )
    db.add(nuevo_tipo)
    await db.commit()  # Operación asincrónica
    await db.refresh(nuevo_tipo)  # Operación asincrónica
    return nuevo_tipo

# Obtener todos los tipos de proveedores
@router.get("/tipoproveedor", response_model=List[TipoProveedorResponse])
async def obtener_tipos_proveedor(db: AsyncSession = Depends(get_db)):
    result = await db.execute(db.query(TipoProveedor))  # Ejecutar la consulta de forma asincrónica
    tipos_proveedor = result.scalars().all()  # Obtener los resultados asincrónicamente
    return tipos_proveedor

# Obtener un tipo de proveedor por su id
@router.get("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
async def obtener_tipo_proveedor_por_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(db.query(TipoProveedor).filter(TipoProveedor.IdTipoProveedor == id))  # Consulta asincrónica
    tipo_proveedor = result.scalars().first()  # Obtener el resultado asincrónicamente
    if tipo_proveedor is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")
    return tipo_proveedor

# Actualizar un tipo de proveedor
@router.put("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
async def actualizar_tipo_proveedor(id: int, tipoProveedorParam: TipoProveedorCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(db.query(TipoProveedor).filter(TipoProveedor.IdTipoProveedor == id))  # Consulta asincrónica
    tipoproveedor = result.scalars().first()  # Obtener el resultado asincrónicamente
    if tipoproveedor is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")
    
    tipoproveedor.NombreTipoProveedor = tipoProveedorParam.NombreTipoProveedor  # Actualiza el campo
    await db.commit()  # Operación asincrónica
    await db.refresh(tipoproveedor)  # Operación asincrónica
    return tipoproveedor

# Eliminar un tipo de proveedor
@router.delete("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
async def eliminar_tipo_proveedor(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(db.query(TipoProveedor).filter(TipoProveedor.IdTipoProveedor == id))  # Consulta asincrónica
    tipo_proveedor = result.scalars().first()  # Obtener el resultado asincrónicamente
    if tipo_proveedor is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")
    
    await db.delete(tipo_proveedor)  # Eliminar de forma asincrónica
    await db.commit()  # Operación asincrónica
    
    return tipo_proveedor  # Devuelve el objeto antes de eliminarlo

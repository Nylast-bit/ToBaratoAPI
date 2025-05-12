from fastapi import APIRouter, HTTPException, Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from app.models.models import TipoProveedor, Proveedor
from app.database import AsyncSessionLocal  # Usar AsyncSessionLocal
from sqlalchemy import select, delete
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.tipoproveedor import TipoProveedorCreate, TipoProveedorResponse
from datetime import datetime



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
async def crear_tipo_proveedor(
    tipoProveedorParam: TipoProveedorCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validaciones
        nombre_limpio = tipoProveedorParam.NombreTipoProveedor.strip()
        
        if nombre_limpio.isdigit():
            raise ValueError("El nombre no puede ser numérico")
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacío")

        # Crear nuevo registro
        nuevo_tipo = TipoProveedor(
            NombreTipoProveedor=nombre_limpio.title(),
            FechaCreacion=datetime.now().replace(tzinfo=None)  # <-- quita la zona horaria
        )
        db.add(nuevo_tipo)
        await db.commit()
        await db.refresh(nuevo_tipo)
        return nuevo_tipo

    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Error de validación",
                "message": str(ve),
                "field": "nombre",
                "value": nombre_limpio
            }
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error interno",
                "message": str(e)
            }
        )


# Obtener todos los tipos de proveedores


@router.get("/tipoproveedor", response_model=List[TipoProveedorResponse])
async def obtener_tipos_proveedor(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(TipoProveedor))
        tipos_proveedor = result.scalars().all()
        return tipos_proveedor


# Obtener un tipo de proveedor por su id
@router.get("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
async def obtener_tipo_proveedor_por_id(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(
            select(TipoProveedor).where(TipoProveedor.IdTipoProveedor == id)
        )
        tipo_proveedor = result.scalars().first()

        if tipo_proveedor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el tipo de proveedor"
            )

        return tipo_proveedor

# Actualizar un tipo de proveedor
@router.put("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
async def actualizar_tipo_proveedor(
    id: int,
    tipoProveedorParam: TipoProveedorCreate,
    db: AsyncSession = Depends(get_db)
):
    async with db as session:
        result = await session.execute(
            select(TipoProveedor).where(TipoProveedor.IdTipoProveedor == id)
        )
        tipoproveedor = result.scalars().first()

        if tipoproveedor is None:
            raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")

        # Validación del nombre
        nombre_limpio = tipoProveedorParam.NombreTipoProveedor.strip()
        if not nombre_limpio:
            raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
        if nombre_limpio.isdigit():
            raise HTTPException(status_code=400, detail="El nombre no puede ser numérico")

        # Actualización
        tipoproveedor.NombreTipoProveedor = nombre_limpio.title()
        await session.commit()
        await session.refresh(tipoproveedor)

        return tipoproveedor


# Eliminar un tipo de proveedor


@router.delete("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
async def eliminar_tipo_proveedor(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # Buscar el tipo de proveedor
        result = await session.execute(
            select(TipoProveedor).where(TipoProveedor.IdTipoProveedor == id)
        )
        tipo_proveedor = result.scalars().first()

        if tipo_proveedor is None:
            raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")

        # Verificar si hay proveedores relacionados
        result_proveedores = await session.execute(
            select(Proveedor).where(Proveedor.IdTipoProveedor == id)
        )
        proveedores_relacionados = result_proveedores.scalars().all()

        if proveedores_relacionados:
            # Eliminar todos los proveedores asociados a ese tipo
            await session.execute(
                delete(Proveedor).where(Proveedor.IdTipoProveedor == id)
            )

        # Eliminar el tipo de proveedor
        await session.delete(tipo_proveedor)
        await session.commit()

        return tipo_proveedor

  # Devuelve el objeto antes de eliminarlo

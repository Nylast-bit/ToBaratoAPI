from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Proveedor,TipoProveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorResponse, ProveedorUpdate
from app.database import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime




router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#Crear un nueva proveedor
@router.post("/proveedor", response_model=ProveedorResponse)
async def crear_proveedor(proveedorParam: ProveedorCreate, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # Validación: Verificar que el tipo de proveedor existe
        tipo_proveedor = await session.execute(select(TipoProveedor).where(TipoProveedor.IdTipoProveedor == proveedorParam.IdTipoProveedor))
        tipo_proveedor = tipo_proveedor.scalars().first()
        if tipo_proveedor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Tipo de proveedor no válido",
                    "code": "INVALID_USER_TYPE",
                    "field": "IdTipoProveedor",
                    "value": proveedorParam.IdTipoProveedor
                }
            )

        # Validaciones adicionales
        if not proveedorParam.Nombre or proveedorParam.Nombre.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "El nombre del proveedor no puede estar vacío",
                    "code": "INVALID_NAME",
                    "field": "Nombre",
                    "value": proveedorParam.Nombre
                }
            )
        
        # Validación para URL del logo (verificar formato)
        if proveedorParam.UrlLogo and not proveedorParam.UrlLogo.startswith('http'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "URL del logo no válida",
                    "code": "INVALID_URL",
                    "field": "UrlLogo",
                    "value": proveedorParam.UrlLogo
                }
            )

        # Validación para URL de la página web (verificar formato)
        if proveedorParam.UrlPaginaWeb and not proveedorParam.UrlPaginaWeb.startswith('http'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "URL de la página web no válida",
                    "code": "INVALID_URL",
                    "field": "UrlPaginaWeb",
                    "value": proveedorParam.UrlPaginaWeb
                }
            )
        
        try:
            nuevo_proveedor = Proveedor(
                IdTipoProveedor=proveedorParam.IdTipoProveedor,
                Nombre=proveedorParam.Nombre.strip(),  # Aseguramos que no haya espacios innecesarios
                UrlLogo=proveedorParam.UrlLogo,
                UrlPaginaWeb=proveedorParam.UrlPaginaWeb,
                EnvioDomicilio=proveedorParam.EnvioDomicilio,
                FechaCreacion=datetime.now().replace(tzinfo=None)
            )
            
            session.add(nuevo_proveedor)
            await session.commit()
            await session.refresh(nuevo_proveedor)
            return nuevo_proveedor
        
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Error al crear proveedor",
                    "code": "PROVEEDOR_CREATION_ERROR",
                    "details": str(e)
                }
            )


#Obtener todos los proveedores
@router.get("/proveedor", response_model=List[ProveedorResponse])
async def obtener_proveedores(db: AsyncSession = Depends(get_db)):
    async with db as session:
        # Realizar la consulta de manera asincrónica
        result = await session.execute(select(Proveedor))
        proveedores = result.scalars().all()
        return proveedores


#Obtener un proveedor por su id
@router.get("/proveedor/{id}", response_model=ProveedorResponse)
async def obtener_proveedor_por_id(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # Realizar la consulta asincrónica
        result = await session.execute(select(Proveedor).where(Proveedor.IdProveedor == id))
        proveedor = result.scalars().first()

        if proveedor is None:
            raise HTTPException(status_code=404, detail="No existe el proveedor")

        return proveedor




#Actualizar un proveedor
@router.put("/proveedor/{id}", response_model=ProveedorResponse)
async def actualizar_proveedor(id: int, proveedorParam: ProveedorUpdate, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # 1. Obtener proveedor existente
        result = await session.execute(select(Proveedor).where(Proveedor.IdProveedor == id))
        proveedor = result.scalars().first()
        if not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Proveedor no encontrado", "id": id}
            )

        try:
            # 2. Obtener solo los campos proporcionados (ignorar None)
            update_data = proveedorParam.model_dump(exclude_unset=True)
            
            # 3. Validaciones específicas
            if "IdTipoProveedor" in update_data:
                # Validar que el tipo de proveedor exista
                result_tipo_proveedor = await session.execute(select(TipoProveedor).where(TipoProveedor.IdTipoProveedor == update_data["IdTipoProveedor"]))
                tipo_proveedor = result_tipo_proveedor.scalars().first()
                if not tipo_proveedor:
                    raise ValueError("El tipo de proveedor especificado no existe")
                
            # 4. Validación de campos adicionales (si es necesario)
            if "UrlLogo" in update_data:
                if not update_data["UrlLogo"].startswith("http"):
                    raise ValueError("La URL del logo debe comenzar con 'http'")
            
            # 5. Aplicar actualizaciones
            for field, value in update_data.items():
                setattr(proveedor, field, value)
            
            await session.commit()
            await session.refresh(proveedor)
            return proveedor
        
        except ValueError as ve:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Error de validación", "message": str(ve)}
            )
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Error al actualizar proveedor",
                    "details": str(e)
                }
            )


#Eliminar un proveedor
@router.delete("/proveedor/{id}", response_model=ProveedorResponse)
async def eliminar_proveedor(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # 1. Obtener proveedor existente
        result = await session.execute(select(Proveedor).where(Proveedor.IdProveedor == id))
        proveedor = result.scalars().first()
        
        if not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe el proveedor"
            )
        
        try:
            # 2. Eliminar el proveedor
            await session.delete(proveedor)
            await session.commit()
            
            return proveedor
        
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Error al eliminar proveedor",
                    "details": str(e)
                }
            )


from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Sucursal, Proveedor
from app.schemas.sucursal import SucursalCreate, SucursalResponse, SucursalUpdate
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime



router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Crear una nueva sucursal
@router.post("/sucursal", response_model=SucursalResponse, status_code=status.HTTP_201_CREATED)
async def crear_sucursal(sucursal: SucursalCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Verificar que el proveedor exista
        result = await db.execute(select(Proveedor).where(Proveedor.IdProveedor == sucursal.IdProveedor))
        proveedor = result.scalar_one_or_none()
        if proveedor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Proveedor no válido",
                    "code": "INVALID_PROVIDER",
                    "field": "IdProveedor",
                    "value": sucursal.IdProveedor
                }
            )

        # Validar que no exista ya una sucursal con el mismo nombre para el mismo proveedor
        result = await db.execute(
            select(Sucursal).where(
                Sucursal.NombreSucursal == sucursal.NombreSucursal,
                Sucursal.IdProveedor == sucursal.IdProveedor
            )
        )
        sucursal_existente = result.scalar_one_or_none()
        if sucursal_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Ya existe una sucursal con ese nombre para el proveedor especificado",
                    "code": "DUPLICATE_BRANCH",
                    "field": "NombreSucursal",
                    "value": sucursal.NombreSucursal
                }
            )

        # Validación de las coordenadas
        # if not (-90 <= sucursal.latitud <= 90):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail={
        #             "error": "Latitud fuera de rango",
        #             "code": "INVALID_LATITUDE",
        #             "field": "latitud",
        #             "value": sucursal.latitud
        #         }
        #     )
        # if not (-180 <= sucursal.longitud <= 180):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail={
        #             "error": "Longitud fuera de rango",
        #             "code": "INVALID_LONGITUDE",
        #             "field": "longitud",
        #             "value": sucursal.longitud
        #         }
        #     )

        # Crear y guardar la nueva sucursal
        nueva_sucursal = Sucursal(
            IdProveedor=sucursal.IdProveedor,
            NombreSucursal=sucursal.NombreSucursal,
            Latitud=sucursal.latitud,
            Longitud=sucursal.longitud,
            FechaCreacion=datetime.now().replace(tzinfo=None)
        )
        db.add(nueva_sucursal)
        await db.commit()
        await db.refresh(nueva_sucursal)

        return nueva_sucursal

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al crear sucursal",
                "code": "SUCURSAL_CREATION_ERROR",
                "details": str(e)
            }   
        )
    
# Obtener todas las sucursales
@router.get("/sucursal", response_model=List[SucursalResponse])
async def obtener_sucursales(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Sucursal))
        sucursales = result.scalars().all()

        if not sucursales:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron sucursales"
            )

        return sucursales

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las sucursales: {str(e)}"
        )


# Obtener una sucursal por su ID
@router.get("/sucursal/{id}", response_model=SucursalResponse)
async def obtener_sucursal(id: int, db: Session = Depends(get_db)):
    # Validación del ID
    if id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El ID de la sucursal debe ser un número positivo", "id": id}
        )

    try:
        sucursal = db.query(Sucursal).filter(Sucursal.IdSucursal == id).first()
        
        if not sucursal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Sucursal no encontrada", "id": id}
            )
        
        return sucursal
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la sucursal: {str(e)}"
        )


# Actualizar una sucursal
@router.put("/sucursal/{id}", response_model=SucursalResponse)
async def actualizar_sucursal(id: int, sucursal_data: SucursalUpdate, db: AsyncSession = Depends(get_db)):
    try:
        # Buscar la sucursal asincrónicamente
        result = await db.execute(select(Sucursal).where(Sucursal.IdSucursal == id))
        sucursal = result.scalar_one_or_none()

        if not sucursal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Sucursal no encontrada", "id": id}
            )

        update_data = sucursal_data.model_dump(exclude_unset=True)

        # Validar que el proveedor exista si se está actualizando
        if "IdProveedor" in update_data:
            prov_result = await db.execute(select(Proveedor).where(Proveedor.IdProveedor == update_data["IdProveedor"]))
            proveedor = prov_result.scalar_one_or_none()
            if not proveedor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "El proveedor especificado no existe",
                        "field": "IdProveedor",
                        "value": update_data["IdProveedor"]
                    }
                )

        # Actualizar los campos
        for field, value in update_data.items():
            setattr(sucursal, field, value)

        await db.commit()
        await db.refresh(sucursal)

        return sucursal

    except HTTPException as http_ex:
        raise http_ex

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(ve)}
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar sucursal", "details": str(e)}
        )


# Eliminar una sucursal
@router.delete("/sucursal/{id}", response_model=SucursalResponse)
async def eliminar_sucursal(id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Buscar la sucursal asincrónicamente
        result = await db.execute(select(Sucursal).where(Sucursal.IdSucursal == id))
        sucursal = result.scalar_one_or_none()

        if not sucursal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Sucursal no encontrada", "id": id}
            )
        
        # Eliminar la sucursal
        await db.delete(sucursal)
        await db.commit()

        return sucursal

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al eliminar sucursal", "details": str(e)}
        )

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Sucursal, Proveedor
from app.schemas.sucursal import SucursalCreate, SucursalResponse, SucursalUpdate
from app.database import AsyncSessionLocal



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
async def crear_sucursal(sucursal: SucursalCreate, db: db_dependency):
    # Verificar que el proveedor exista
    if not db.query(Proveedor).get(sucursal.IdProveedor):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Proveedor no válido",
                "code": "INVALID_PROVIDER",
                "field": "IdProveedor",
                "value": sucursal.IdProveedor
            }
        )
    
    try:
        nueva_sucursal = Sucursal(
            IdProveedor=sucursal.IdProveedor,
            NombreSucursal=sucursal.NombreSucursal,
            latitud=sucursal.latitud,
            longitud=sucursal.longitud
        )
        db.add(nueva_sucursal)
        db.commit()
        db.refresh(nueva_sucursal)
        return nueva_sucursal
    except Exception as e:
        db.rollback()
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
async def obtener_sucursales(db: db_dependency):
    sucursales = db.query(Sucursal).all()
    return sucursales

# Obtener una sucursal por su ID
@router.get("/sucursal/{id}", response_model=SucursalResponse)
async def obtener_sucursal(id: int, db: db_dependency):
    sucursal = db.query(Sucursal).filter(Sucursal.IdSucursal == id).first()
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Sucursal no encontrada", "id": id}
        )
    return sucursal

# Actualizar una sucursal
@router.put("/sucursal/{id}", response_model=SucursalResponse)
async def actualizar_sucursal(id: int, sucursal_data: SucursalUpdate, db: db_dependency):
    sucursal = db.query(Sucursal).filter(Sucursal.IdSucursal == id).first()
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Sucursal no encontrada", "id": id}
        )
    
    try:
        update_data = sucursal_data.model_dump(exclude_unset=True)
        
        # Validar proveedor si se está actualizando
        if "IdProveedor" in update_data:
            if not db.query(Proveedor).get(update_data["IdProveedor"]):
                raise ValueError("El proveedor especificado no existe")
        
        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(sucursal, field, value)
        
        db.commit()
        db.refresh(sucursal)
        return sucursal
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(ve)}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al actualizar sucursal",
                "details": str(e)
            }
        )

# Eliminar una sucursal
@router.delete("/sucursal/{id}", response_model=SucursalResponse)
async def eliminar_sucursal(id: int, db: db_dependency):
    sucursal = db.query(Sucursal).filter(Sucursal.IdSucursal == id).first()
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Sucursal no encontrada", "id": id}
        )
    
    try:
        db.delete(sucursal)
        db.commit()
        return sucursal
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al eliminar sucursal",
                "details": str(e)
            }
        )
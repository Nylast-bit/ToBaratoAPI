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
async def crear_sucursal(sucursal: SucursalCreate, db: Session = Depends(get_db)):
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

    # Validar que no exista ya una sucursal con el mismo nombre para el mismo proveedor
    if db.query(Sucursal).filter(Sucursal.NombreSucursal == sucursal.NombreSucursal, Sucursal.ProveedorId == sucursal.IdProveedor).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Ya existe una sucursal con ese nombre para el proveedor especificado",
                "code": "DUPLICATE_BRANCH",
                "field": "NombreSucursal",
                "value": sucursal.NombreSucursal
            }
        )

    # Validación de las coordenadas (latitud y longitud)
    if not (-90 <= sucursal.latitud <= 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Latitud fuera de rango",
                "code": "INVALID_LATITUDE",
                "field": "latitud",
                "value": sucursal.latitud
            }
        )
    if not (-180 <= sucursal.longitud <= 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Longitud fuera de rango",
                "code": "INVALID_LONGITUDE",
                "field": "longitud",
                "value": sucursal.longitud
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
async def obtener_sucursales(db: Session = Depends(get_db)):
    try:
        sucursales = db.query(Sucursal).all()
        
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
async def actualizar_sucursal(id: int, sucursal_data: SucursalUpdate, db: db_dependency):
    sucursal = db.query(Sucursal).filter(Sucursal.IdSucursal == id).first()
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Sucursal no encontrada", "id": id}
        )
    
    try:
        # Validación de los datos antes de proceder con la actualización
        update_data = sucursal_data.model_dump(exclude_unset=True)
        
        # Validar que el proveedor exista si se va a actualizar
        if "IdProveedor" in update_data:
            if not db.query(Proveedor).get(update_data["IdProveedor"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": "El proveedor especificado no existe", "field": "IdProveedor", "value": update_data["IdProveedor"]}
                )
        
        # Si todo está bien, aplicamos las actualizaciones a los campos
        for field, value in update_data.items():
            setattr(sucursal, field, value)
        
        db.commit()
        db.refresh(sucursal)
        return sucursal
    
    except HTTPException as http_ex:
        # Si se lanza una HTTPException, se pasa tal cual sin cambios
        raise http_ex
    
    except ValueError as ve:
        # Si el error es por algún valor específico, retornamos el detalle
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(ve)}
        )
    
    except Exception as e:
        # En caso de cualquier otra excepción, hacemos rollback y lanzamos un error genérico
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar sucursal", "details": str(e)}
        )


# Eliminar una sucursal
@router.delete("/sucursal/{id}", response_model=SucursalResponse)
async def eliminar_sucursal(id: int, db: db_dependency):
    # Buscar la sucursal por ID
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
        # Si ocurre cualquier otro error, hacemos un rollback y lanzamos el error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al eliminar sucursal", "details": str(e)}
        )

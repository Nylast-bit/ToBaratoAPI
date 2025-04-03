from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Proveedor,TipoProveedor
from app.database import SessionLocal
from app.schemas.proveedor import ProveedorCreate, ProveedorResponse, ProveedorUpdate


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#Crear un nueva unidad de medida
@router.post("/proveedor", response_model=ProveedorResponse)
def crear_proveedor(proveedorParam: ProveedorCreate, db: Session = Depends(get_db)):
    if not db.query(TipoProveedor).get(proveedorParam.IdTipoProveedor):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Tipo de proveedor no válido",
                "code": "INVALID_USER_TYPE",
                "field": "IdTipoProveedor",
                "value": proveedorParam.IdTipoProveedor
            }
        )
    
    try:
        nuevo_proveedor = Proveedor(
        IdTipoProveedor = proveedorParam.IdTipoProveedor, # ← Usa el nombre correcto
        Nombre = proveedorParam.Nombre, # ← Usa el nombre correcto
        UrlLogo = proveedorParam.UrlLogo, # ← Usa el nombre correcto
        UrlPaginaWeb = proveedorParam.UrlPaginaWeb, # ← Usa el nombre correcto
        EnvioDomicilio = proveedorParam.EnvioDomicilio # ← Usa el nombre correcto

        )
        db.add(nuevo_proveedor)
        db.commit()
        db.refresh(nuevo_proveedor)
        return nuevo_proveedor
    
        
    except Exception as e:
        db.rollback()
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
def obtener_proveedores(db: Session = Depends(get_db)):
    proveedores = db.query(Proveedor).all()
    return proveedores

#Obtener un proveedor por su id
@router.get("/proveedor/{id}", response_model=ProveedorResponse)
def obtener_proveedor_por_id(id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.IdProveedor == id).first()
    if proveedor is None:
        raise HTTPException(status_code=404, detail="No existe el proveedor")
    return proveedor   

#Actualizar un proveedor
@router.put("/proveedor/{id}", response_model=ProveedorResponse)
def actualizar_proveedor(id: int, proveedorParam: ProveedorUpdate, db: Session = Depends(get_db)):
    # 1. Obtener proveedor existente
    proveedor = db.query(Proveedor).filter(Proveedor.IdProveedor == id).first()
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
            if not db.query(TipoProveedor).get(update_data["IdTipoProveedor"]):
                raise ValueError("El tipo de proveedor especificado no existe")
        
        
        # 4. Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(proveedor, field, value)
        
        db.commit()
        db.refresh(proveedor)
        return proveedor
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al actualizar proveedor",
                "details": str(e)
            }
        )

#Eliminar un proveedor
@router.delete("/proveedor/{id}", response_model=ProveedorResponse)
def eliminar_proveedor(id: int, db: Session = Depends(get_db)):
    proveedor = db.query(Proveedor).filter(Proveedor.IdProveedor == id).first()
    if proveedor is None:
        raise HTTPException(status_code=404, detail="No existe el proveedor")

    db.delete(proveedor)
    db.commit()
    
    return proveedor  # ← Devuelve el objeto antes de eliminarlo en la sesión


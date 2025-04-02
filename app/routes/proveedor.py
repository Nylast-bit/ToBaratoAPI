from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Proveedor,TipoProveedor
from app.database import SessionLocal
from app.schemas.proveedor import ProveedorCreate, ProveedorResponse


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


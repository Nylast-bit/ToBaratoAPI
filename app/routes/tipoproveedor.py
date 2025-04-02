from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import TipoProveedor
from app.database import SessionLocal
from app.schemas.tipoproveedor import TipoProveedorCreate, TipoProveedorResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#Crear un nuevo tipo de proveedor
@router.post("/tipoproveedor", response_model=TipoProveedorResponse)
def crear_tipo_proveedor(tipoProveedorParam: TipoProveedorCreate, db: Session = Depends(get_db)):
    nuevo_tipo = TipoProveedor(
        NombreTipoProveedor = tipoProveedorParam.NombreTipoProveedor  # ← Usa el nombre correcto
    )
    db.add(nuevo_tipo)
    db.commit()
    db.refresh(nuevo_tipo)
    return nuevo_tipo


#Obtener todos los tipos de proveedores
@router.get("/tipoproveedor", response_model=List[TipoProveedorResponse])
def obtener_tipos_proveedor(db: Session = Depends(get_db)):
    tipos_proveedor = db.query(TipoProveedor).all()
    return tipos_proveedor

#Obtener un tipo de proveedor por su id
@router.get("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
def obtener_tipo_proveedor_por_id(id: int, db: Session = Depends(get_db)):
    tipo_proveedor = db.query(TipoProveedor).filter(TipoProveedor.IdTipoProveedor == id).first()
    if tipo_proveedor is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")
    return tipo_proveedor

#Actualizar un tipo de proveedor
@router.put("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
def actualizar_tipo_proveedor(id: int, tipoProveedorParam: TipoProveedorCreate, db: Session = Depends(get_db)):
    tipoproveedor = db.query(TipoProveedor).filter(TipoProveedor.IdTipoProveedor == id).first()
    if tipoproveedor is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")
    tipoproveedor.NombreTipoProveedor = tipoProveedorParam.NombreTipoProveedor  # ← Usa el nombre correcto 
    db.commit()
    db.refresh(tipoproveedor)
    return tipoproveedor

#Eliminar un tipo de proveedor
@router.delete("/tipoproveedor/{id}", response_model=TipoProveedorResponse)
def eliminar_tipo_proveedor(id: int, db: Session = Depends(get_db)):
    tipo_proveedor = db.query(TipoProveedor).filter(TipoProveedor.IdTipoProveedor == id).first()
    if tipo_proveedor is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de proveedor")

    db.delete(tipo_proveedor)
    db.commit()
    
    return tipo_proveedor  # ← Devuelve el objeto antes de eliminarlo en la sesión

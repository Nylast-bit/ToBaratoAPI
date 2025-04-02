from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Producto
from app.database import SessionLocal
from app.schemas.producto import ProductoCreate, ProductoResponse


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/producto", response_model=ProductoResponse)
def crear_producto(productoParam: ProductoCreate, db: Session = Depends(get_db)):
    nuevo_producto = Producto(
        IdCategoria = productoParam.IdCategoria, # ← Usa el nombre correcto
        IdUnidadMedida = productoParam.IdUnidadMedida, # ← Usa el nombre correcto
        Nombre = productoParam.Nombre, # ← Usa el nombre correcto
        UrlImagen = productoParam.UrlImagen, # ← Usa el nombre correcto
        Descripcion = productoParam.Descripcion # ← Usa el nombre correcto
    )
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


# Obtener todos los productos   
@router.get("/producto", response_model=List[ProductoResponse])
def obtener_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productos
        
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import ProductoProveedor
from app.database import SessionLocal
from app.schemas.productoproveedor import ProductoProveedorCreate, ProductoProveedorResponse


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/productoproveedor", response_model=ProductoProveedorResponse)
def crear_listaproducto(productoproveedorParam: ProductoProveedorCreate, db: Session = Depends(get_db)):
    nuevo_productoproveedor= ProductoProveedor(
        IdProducto = productoproveedorParam.IdProveedor, # ← Usa el nombre correcto
        IdProveedor = productoproveedorParam.IdProveedor, # ← Usa el nombre correcto
        Precio = productoproveedorParam.Precio, # ← Usa el nombre correcto
        PrecioOferta = productoproveedorParam.PrecioOferta, # ← Usa el nombre correcto
        DescripcionOferta = productoproveedorParam.DescripcionOferta, # ← Usa el nombre correcto
        FechaOferta = productoproveedorParam.FechaOferta, # ← Usa el nombre correcto
        FechaPrecio = productoproveedorParam.FechaPrecio, # ← Usa el nombre correcto



    )
    db.add(nuevo_productoproveedor)
    db.commit()
    db.refresh(nuevo_productoproveedor)
    return nuevo_productoproveedor


# Obtener todos los productos
@router.get("/productoproveedor", response_model=List[ProductoProveedorResponse])
def obtener_productoproveedor(db: Session = Depends(get_db)):
    productoproveedor = db.query(ProductoProveedor).all()
    if not productoproveedor:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productoproveedor
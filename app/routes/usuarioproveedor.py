from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import UsuarioProveedor
from app.database import SessionLocal
from app.schemas.usuarioproveedor import UsuarioProveedorCreate, UsuarioProveedorResponse


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/usuarioproveedor", response_model=UsuarioProveedorResponse)
def crear_listaproducto(usuarioProveedorParam: UsuarioProveedorCreate, db: Session = Depends(get_db)):
    nuevo_usuarioproveedor= UsuarioProveedor(
        IdProveedor = usuarioProveedorParam.IdProveedor, # ← Usa el nombre correcto
        IdUsuario = usuarioProveedorParam.IdUsuario, # ← Usa el nombre correcto 
        ProductosComprados = usuarioProveedorParam.ProductosComprados, # ← Usa el nombre correcto
        FechaUltimaCompra = usuarioProveedorParam.FechaUltimaCompra, # ← Usa el nombre correcto
        Preferencia = usuarioProveedorParam.Preferencia, # ← Usa el nombre correcto


    )
    db.add(nuevo_usuarioproveedor)
    db.commit()
    db.refresh(nuevo_usuarioproveedor)
    return nuevo_usuarioproveedor


# Obtener todos los productos
@router.get("/usuarioproveedor", response_model=List[UsuarioProveedorResponse])
def obtener_usuarioproveedor(db: Session = Depends(get_db)):
    usuarioproveedor = db.query(UsuarioProveedor).all()
    if not usuarioproveedor:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return usuarioproveedor
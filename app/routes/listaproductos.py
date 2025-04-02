from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import ListaProducto
from app.database import SessionLocal
from app.schemas.listaproductos import ListaProductoCreate, ListaProductoResponse


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/listaproducto", response_model=ListaProductoResponse)
def crear_listaproducto(listaProductoParam: ListaProductoCreate, db: Session = Depends(get_db)):
    nueva_listaproducto = ListaProducto(
        IdLista = listaProductoParam.IdLista, # ← Usa el nombre correcto
        IdProducto = listaProductoParam.IdProducto, # ← Usa el nombre correcto
        PrecioActual = listaProductoParam.PrecioActual, # ← Usa el nombre correcto
        Cantidad = listaProductoParam.Cantidad, # ← Usa el nombre correcto

    )
    db.add(nueva_listaproducto)
    db.commit()
    db.refresh(nueva_listaproducto)
    return nueva_listaproducto

# Obtener todos los productos   
@router.get("/listaproducto", response_model=List[ListaProductoResponse])   
def obtener_listaproductos(db: Session = Depends(get_db)):
    listaproductos = db.query(ListaProducto).all()
    if not listaproductos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return listaproductos
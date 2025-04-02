from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Lista
from app.database import SessionLocal
from app.schemas.lista import ListaCreate, ListaResponse


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/lista", response_model=ListaResponse)
def crear_lista(listaParam: ListaCreate, db: Session = Depends(get_db)):
    nuevo_lista = Lista(
        IdUsuario = listaParam.IdUsuario, # ← Usa el nombre correcto
        IdProveedor = listaParam.IdProveedor, # ← Usa el nombre correcto
        Nombre = listaParam.Nombre, # ← Usa el nombre correcto
        PrecioTotal = listaParam.PrecioTotal # ← Usa el nombre correcto
    )
    db.add(nuevo_lista)
    db.commit()
    db.refresh(nuevo_lista)
    return nuevo_lista
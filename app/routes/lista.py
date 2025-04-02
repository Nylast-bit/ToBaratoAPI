from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Lista, Usuario, Proveedor
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
    # Verificaciones separadas con mensajes de error específicos
    errors = []

# Verificar si el proveedor existe
    if not db.query(Proveedor).get(listaParam.IdProveedor):
        errors.append({
            "error": "Proveedor no encontrado",
            "code": "INVALID_PROVIDER",
            "field": "IdProveedor",
            "value": listaParam.IdProveedor,
            "suggestion": "Verifique el ID del proveedor en la tabla Proveedor"
        })

    # Verificar si el usuario existe
    if not db.query(Usuario).get(listaParam.IdUsuario):
        errors.append({
            "error": "Usuario no encontrado",
            "code": "INVALID_USER",
            "field": "IdUsuario",
            "value": listaParam.IdUsuario,
            "suggestion": "Verifique el ID del usuario en la tabla Usuario"
        })

    # si hay algún error en los datos de entrada, lanza una excepción
    if errors:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": "Error de validación en los datos de entrada",
            "errors": errors,
            "total_errors": len(errors),
            "validated": False
        }
    )
    
    try:
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

#Obtener todas las listas   
@router.get("/lista", response_model=List[ListaResponse])
def obtener_listas(db: Session = Depends(get_db)):
    listas = db.query(Lista).all()
    return listas

#
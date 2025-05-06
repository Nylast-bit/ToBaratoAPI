from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Lista, Usuario, Proveedor
from app.schemas.lista import ListaCreate, ListaResponse, ListaUpdate
from app.database import AsyncSessionLocal



router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
       await db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/lista", response_model=ListaResponse)
async def crear_lista(listaParam: ListaCreate, db: Session = Depends(get_db)):
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
async def obtener_listas(db: Session = Depends(get_db)):
    listas = db.query(Lista).all()
    return listas

#Obtener una lista por su id  
@router.get("/lista/{id}", response_model=ListaResponse)        
async def obtener_lista_por_id(id: int, db: Session = Depends(get_db)):
    lista = db.query(Lista).filter(Lista.IdLista == id).first()
    if lista is None:
        raise HTTPException(status_code=404, detail="No existe la lista") 
    return lista

#Actualizar una lista por su id
@router.put("/lista/{id}", response_model=ListaResponse)
async def actualizar_lista(id: int, listaParam: ListaUpdate, db: Session = Depends(get_db)):
    lista = db.query(Lista).filter(Lista.IdLista == id).first()
    if not lista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Lista no encontrada", "id": id}
        )
    
    try:
        update_data = listaParam.model_dump(exclude_unset=True)
        
        # Validaciones
        if "IdUsuario" in update_data:
            if not db.query(Usuario).get(update_data["IdUsuario"]):
                raise ValueError("El usuario especificado no existe")
        
        if "IdProveedor" in update_data:
            if not db.query(Proveedor).get(update_data["IdProveedor"]):
                raise ValueError("El proveedor especificado no existe")
        
        if "PrecioTotal" in update_data and update_data["PrecioTotal"] < 0:
            raise ValueError("El precio total no puede ser negativo")
        
        # Actualización
        for field, value in update_data.items():
            setattr(lista, field, value)
        
        db.commit()
        db.refresh(lista)
        return lista
        
    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error de validación", "message": str(ve)}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar lista", "details": str(e)}
        )
    
#Eliminar una lista por su id
@router.delete("/lista/{id}", response_model=ListaResponse)
async def eliminar_lista(id: int, db: Session = Depends(get_db)):
    lista = db.query(Lista).filter(Lista.IdLista == id).first()
    if lista is None:
        raise HTTPException(status_code=404, detail="No existe la lista")

    db.delete(lista)
    db.commit()    
    return lista  # ← Devuelve el objeto antes de eliminarlo en la sesión
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Lista, Usuario, Proveedor
from app.schemas.lista import ListaCreate, ListaResponse, ListaUpdate
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime





router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
       await db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva lista
@router.post("/lista", response_model=ListaResponse)
async def crear_lista(listaParam: ListaCreate, db: AsyncSession = Depends(get_db)):
    # Verificaciones separadas con mensajes de error específicos
    errors = []

    # Verificar si el proveedor existe
    result = await db.execute(select(Proveedor).where(Proveedor.IdProveedor == listaParam.IdProveedor))
    proveedor = result.scalar_one_or_none()
    if not proveedor:
        errors.append({
            "error": "Proveedor no encontrado",
            "code": "INVALID_PROVIDER",
            "field": "IdProveedor",
            "value": listaParam.IdProveedor,
            "suggestion": "Verifique el ID del proveedor en la tabla Proveedor"
        })

    # Verificar si el usuario existe
    result = await db.execute(select(Usuario).where(Usuario.IdUsuario == listaParam.IdUsuario))
    usuario = result.scalar_one_or_none()
    if not usuario:
        errors.append({
            "error": "Usuario no encontrado",
            "code": "INVALID_USER",
            "field": "IdUsuario",
            "value": listaParam.IdUsuario,
            "suggestion": "Verifique el ID del usuario en la tabla Usuario"
        })

    # Si hay algún error en los datos de entrada, lanza una excepción
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
        # Crear el nuevo objeto lista
        nuevo_lista = Lista(
            IdUsuario=listaParam.IdUsuario,
            IdProveedor=listaParam.IdProveedor,
            Nombre=listaParam.Nombre,
            PrecioTotal=listaParam.PrecioTotal,
            FechaCreacion=datetime.now().replace(tzinfo=None)

        )

        # Agregar a la base de datos y confirmar
        db.add(nuevo_lista)
        await db.commit()
        await db.refresh(nuevo_lista)

        return nuevo_lista

    except Exception as e:
        # Si ocurre algún error, hacemos rollback y lanzamos una excepción
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al crear lista",
                "code": "LIST_CREATION_ERROR",
                "details": str(e)
            }
        )
 

#Obtener todas las listas   
@router.get("/lista", response_model=List[ListaResponse])
async def obtener_listas(db: AsyncSession = Depends(get_db)):
    # Ejecutar la consulta asincrónica para obtener todas las listas
    result = await db.execute(select(Lista))
    listas = result.scalars().all()  # Obtener todas las listas
    
    return listas


#Obtener una lista por su id  
@router.get("/lista/{id}", response_model=ListaResponse)
async def obtener_lista_por_id(id: int, db: AsyncSession = Depends(get_db)):
    # Realizamos la consulta asincrónica
    result = await db.execute(select(Lista).filter(Lista.IdLista == id))
    lista = result.scalar_one_or_none()
    
    if lista is None:
        raise HTTPException(status_code=404, detail="No existe la lista")
    
    return lista

#Actualizar una lista por su id
@router.put("/lista/{id}", response_model=ListaResponse)
async def actualizar_lista(id: int, listaParam: ListaUpdate, db: AsyncSession = Depends(get_db)):
    # Obtener la lista existente
    result = await db.execute(select(Lista).where(Lista.IdLista == id))
    lista = result.scalar_one_or_none()
    if not lista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Lista no encontrada", "id": id}
        )
    
    try:
        # Obtener solo los campos proporcionados
        update_data = listaParam.model_dump(exclude_unset=True)

        # Validaciones
        if "IdUsuario" in update_data:
            result = await db.execute(select(Usuario).where(Usuario.IdUsuario == update_data["IdUsuario"]))
            usuario = result.scalar_one_or_none()
            if not usuario:
                raise ValueError("El usuario especificado no existe")

        if "IdProveedor" in update_data:
            result = await db.execute(select(Proveedor).where(Proveedor.IdProveedor == update_data["IdProveedor"]))
            proveedor = result.scalar_one_or_none()
            if not proveedor:
                raise ValueError("El proveedor especificado no existe")

        if "PrecioTotal" in update_data and update_data["PrecioTotal"] < 0:
            raise ValueError("El precio total no puede ser negativo")

        # Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(lista, field, value)

        # Confirmar cambios
        await db.commit()
        await db.refresh(lista)
        return lista
        
    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error de validación", "message": str(ve)}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar lista", "details": str(e)}
        ) 

#Eliminar una lista por su id
@router.delete("/lista/{id}", response_model=ListaResponse)
async def eliminar_lista(id: int, db: AsyncSession = Depends(get_db)):
    # Buscar la lista por ID de forma asincrónica
    result = await db.execute(select(Lista).where(Lista.IdLista == id))
    lista = result.scalar_one_or_none()
    if lista is None:
        raise HTTPException(status_code=404, detail="No existe la lista")

    try:
        # Eliminar la lista de manera asincrónica
        await db.delete(lista)
        await db.commit()  # Confirmar cambios

        return lista  # Devuelve el objeto antes de eliminarlo en la sesión
    
    except Exception as e:
        await db.rollback()  # Revertir en caso de error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al eliminar lista", "details": str(e)}
        )
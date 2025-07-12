from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import ListaProducto
from app.schemas.listaproductos import ListaProductoCreate, ListaProductoResponse, ListaProductoUpdate
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, extract, desc

from sqlalchemy.future import select
from app.models.models import Producto, ListaProducto, Lista, Proveedor, Sucursal, Categoria

router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear una nueva lista de productos
@router.post("/listaproducto", response_model=ListaProductoResponse)
async def crear_listaproducto(listaProductoParam: ListaProductoCreate, db: AsyncSession = Depends(get_db)):
    nueva_listaproducto = ListaProducto(
        IdLista = listaProductoParam.IdLista,
        IdProducto = listaProductoParam.IdProducto,
        PrecioActual = listaProductoParam.PrecioActual,
        Cantidad = listaProductoParam.Cantidad,
    )
    db.add(nueva_listaproducto)
    await db.commit()  # Esperar que la transacción se complete
    await db.refresh(nueva_listaproducto)  # Esperar que el objeto se actualice con los valores de la base de datos
    return nueva_listaproducto

# Obtener todos las listas de productos
@router.get("/listaproducto", response_model=List[ListaProductoResponse])   
async def obtener_listaproductos(db: AsyncSession = Depends(get_db)):
    # Realizar la consulta de manera asincrónica
    result = await db.execute(select(ListaProducto))
    listaproductos = result.scalars().all()
    
    if not listaproductos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    
    return listaproductos

# Obtener una lista de productos por ID
@router.get("/listas/{id_lista}/productos/{id_producto}", response_model=ListaProductoResponse)
async def obtener_producto_lista(
    id_lista: int,
    id_producto: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene un producto específico de una lista por sus IDs compuestos de forma asincrónica
    """
    # Realizar la consulta de manera asincrónica
    result = await db.execute(select(ListaProducto).filter(
        ListaProducto.IdLista == id_lista,
        ListaProducto.IdProducto == id_producto
    ))
    
    # Obtener el primer resultado de la consulta
    relacion = result.scalars().first()
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "IdLista": id_lista,
                "IdProducto": id_producto
            }
        )
    
    return relacion





#Actualizar un producto
@router.put("/listas/{id_lista}/productos/{id_producto}", response_model=ListaProductoResponse)
async def actualizar_producto_lista(
    id_lista: int,
    id_producto: int,
    datos: ListaProductoUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Realizar la consulta de manera asincrónica
    result = await db.execute(select(ListaProducto).filter(
        ListaProducto.IdLista == id_lista,
        ListaProducto.IdProducto == id_producto
    ))
    
    relacion = result.scalars().first()
    
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    
    # Obtener los datos de actualización y aplicar los cambios
    update_data = datos.model_dump(exclude_unset=True)
    
    for campo, valor in update_data.items():
        setattr(relacion, campo, valor)
    
    # Guardar los cambios en la base de datos
    await db.commit()
    await db.refresh(relacion)
    
    return relacion

#eliminar un producto de una lista
@router.delete("/listas/{id_lista}/productos/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto_lista(
    id_lista: int,
    id_producto: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina un producto de una lista usando los IDs compuestos de manera asincrónica
    """
    # Realizar la consulta de manera asincrónica
    result = await db.execute(select(ListaProducto).filter(
        ListaProducto.IdLista == id_lista,
        ListaProducto.IdProducto == id_producto
    ))
    
    relacion = result.scalars().first()
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "IdLista": id_lista,
                "IdProducto": id_producto
            }
        )
    
    try:
        await db.delete(relacion)  # Asincrónico
        await db.commit()          # Asincrónico
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        await db.rollback()        # Asincrónico
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al eliminar relación",
                "details": str(e)
            }
        )


@router.get("/productosdelista/{id_lista}", response_model=List[ListaProductoResponse])
async def obtener_productos_de_lista(
    id_lista: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene todos los productos asociados a una lista específica de forma asincrónica
    """
    result = await db.execute(
        select(ListaProducto).where(ListaProducto.IdLista == id_lista)
    )
    
    productos = result.scalars().all()

    if not productos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "No se encontraron productos para la lista",
                "IdLista": id_lista
            }
        )

    return productos


@router.delete("/productosdelista/{id_lista}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_productos_de_lista(
    id_lista: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina todos los productos asociados a una lista específica usando instancia + db.delete
    """
    # Buscar los productos de la lista
    result = await db.execute(
        select(ListaProducto).where(ListaProducto.IdLista == id_lista)
    )
    productos = result.scalars().all()

    if not productos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron productos con IdLista {id_lista}"
        )

    # Eliminar uno por uno usando db.delete
    for producto in productos:
        await db.delete(producto)

    await db.commit()


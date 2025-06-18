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


@router.get("/dashboard/insights")
async def obtener_insights(db: AsyncSession = Depends(get_db)):
    insights = []

    # Productos más comprados por proveedor
    query1 = (
        select(
            Producto.Nombre,
            Proveedor.Nombre,
            func.count().label("Total")
        )
        .join(ListaProducto, Producto.IdProducto == ListaProducto.IdProducto)
        .join(Lista, Lista.IdLista == ListaProducto.IdLista)
        .join(Proveedor, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Producto.Nombre, Proveedor.Nombre)
        .order_by(desc("Total"))
        .limit(10)
    )
    result1 = await db.execute(query1)
    productos_comprados = [
        {"producto": r[0], "proveedor": r[1], "veces_comprado": r[2]} for r in result1
    ]
    insights.append({"Productos más comprados por proveedor": productos_comprados})

    # Días con más compras de productos (y proveedor que más aparece)
    query2 = (
        select(
            func.to_char(Lista.FechaCreacion, 'Day').label("dia_semana"),
            func.count().label("total")
        )
        .group_by("dia_semana")
        .order_by(desc("total"))
    )
    result2 = await db.execute(query2)
    dias_populares = [
        {"dia": r[0].strip(), "compras": r[1]} for r in result2
    ]

    query2b = (
        select(Proveedor.Nombre, func.count(Lista.IdProveedor).label("total"))
        .join(Lista, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Proveedor.Nombre)
        .order_by(desc("total"))
        .limit(1)
    )
    proveedor_mas_aparece = (await db.execute(query2b)).first()
    insights.append({"Días con más compras de productos": dias_populares, "Proveedor más frecuente": proveedor_mas_aparece[0] if proveedor_mas_aparece else None})

    # Proveedor con más listas
    query3 = (
        select(Proveedor.Nombre, func.count().label("total"))
        .join(Lista, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Proveedor.Nombre)
        .order_by(desc("total"))
    )
    result3 = await db.execute(query3)
    insights.append({"Proveedores con más listas": [
        {"proveedor": r[0], "listas": r[1]} for r in result3
    ]})

    # Cantidad de sucursales por proveedor
    query4 = (
        select(Proveedor.Nombre, func.count().label("total"))
        .join(Sucursal, Sucursal.IdProveedor == Proveedor.IdProveedor)
        .group_by(Proveedor.Nombre)
    )
    result4 = await db.execute(query4)
    insights.append({"Sucursales por proveedor": [
        {"proveedor": r[0], "sucursales": r[1]} for r in result4
    ]})

    # Tendencia semanal de compras
    query5 = (
        select(func.date_trunc('week', Lista.FechaCreacion).label("semana"), func.count().label("total"))
        .group_by("semana")
        .order_by("semana")
    )
    result5 = await db.execute(query5)
    insights.append({"Tendencia semanal": [
        {"semana": r[0].strftime("%Y-%m-%d"), "listas": r[1]} for r in result5
    ]})

    # Precio promedio de listas por proveedor
    query6 = (
        select(Proveedor.Nombre, func.avg(Lista.PrecioTotal).label("promedio"))
        .join(Lista, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Proveedor.Nombre)
    )
    result6 = await db.execute(query6)
    insights.append({"Precio promedio por proveedor": [
        {"proveedor": r[0], "promedio": float(r[1])} for r in result6
    ]})

    # Cantidad promedio de productos por lista de proveedor
    # Cantidad promedio de productos por lista de proveedor
    sub = (
        select(Lista.IdProveedor, func.count(ListaProducto.IdProducto).label("cantidad"))
        .join(ListaProducto, Lista.IdLista == ListaProducto.IdLista)
        .group_by(Lista.IdLista, Lista.IdProveedor)
    ).subquery()

    query7 = (
        select(Proveedor.Nombre, func.avg(sub.c.cantidad).label("promedio"))
        .join(sub, sub.c.IdProveedor == Proveedor.IdProveedor)
        .group_by(Proveedor.Nombre)
    )

    result7 = await db.execute(query7)
    insights.append({"Cantidad promedio de productos por lista (por proveedor)": [
        {"proveedor": r[0], "promedio": float(r[1])} for r in result7
    ]})

    # Producto más comprado por categoría
    query8 = (
        select(Categoria.NombreCategoria, Producto.Nombre, func.count().label("Total"))
        .join(Producto, Categoria.IdCategoria == Producto.IdCategoria)
        .join(ListaProducto, Producto.IdProducto == ListaProducto.IdProducto)
        .group_by(Categoria.NombreCategoria, Producto.Nombre)
        .order_by(Categoria.NombreCategoria, desc("Total"))
    )
    result8 = await db.execute(query8)
    productos_categoria = {}
    for nombre_cat, nombre_prod, total in result8:
        if nombre_cat not in productos_categoria:
            productos_categoria[nombre_cat] = {"producto": nombre_prod, "veces_comprado": total}
    insights.append({"Producto más comprado por categoría": productos_categoria})

    # Mapa de calor por hora del día
    query9 = (
        select(extract('hour', Lista.FechaCreacion).label("hora"), func.count().label("total"))
        .group_by("hora")
        .order_by("hora")
    )
    result9 = await db.execute(query9)
    insights.append({"Mapa de calor por hora": [
        {"hora": int(r[0]), "total": r[1]} for r in result9
    ]})

    return insights



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


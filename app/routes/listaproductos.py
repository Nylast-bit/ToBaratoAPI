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

    # Productos más comprados por proveedor (con IDs)
    query1 = (
        select(
            Producto.IdProducto,
            Producto.Nombre,
            Proveedor.IdProveedor,
            Proveedor.Nombre,
            func.count().label("Total")
        )
        .join(ListaProducto, Producto.IdProducto == ListaProducto.IdProducto)
        .join(Lista, Lista.IdLista == ListaProducto.IdLista)
        .join(Proveedor, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Producto.IdProducto, Producto.Nombre, Proveedor.IdProveedor, Proveedor.Nombre)
        .order_by(desc("Total"))
        .limit(10)
    )
    result1 = await db.execute(query1)
    productos_comprados = [
        {
            "id_producto": r[0],
            "producto": r[1],
            "id_proveedor": r[2],
            "proveedor": r[3],
            "veces_comprado": r[4],
        } for r in result1
    ]
    insights.append({"Productos más comprados por proveedor": productos_comprados})

    # Días con más compras de productos (con detalles)
    query2 = (
        select(
            func.to_char(Lista.FechaCreacion, 'Day').label("dia_semana"),
            Producto.IdProducto,
            Producto.Nombre,
            func.count().label("total")
        )
        .join(ListaProducto, Lista.IdLista == ListaProducto.IdLista)
        .join(Producto, Producto.IdProducto == ListaProducto.IdProducto)
        .group_by("dia_semana", Producto.IdProducto, Producto.Nombre)
        .order_by(desc("total"))
        .limit(10)
    )
    result2 = await db.execute(query2)
    dias_populares = [
        {
            "dia": r[0].strip(),
            "id_producto": r[1],
            "producto": r[2],
            "compras": r[3]
        } for r in result2
    ]

    query2b = (
        select(Proveedor.Nombre, func.count(Lista.IdProveedor).label("total"))
        .join(Lista, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Proveedor.Nombre)
        .order_by(desc("total"))
        .limit(3)
    )
    result2b = await db.execute(query2b)
    proveedores_frecuentes = [r[0] for r in result2b]
    insights.append({"Días con más compras de productos": dias_populares, "Top 3 Proveedores más frecuentes": proveedores_frecuentes})

    # Tendencia semanal de compras con productos más frecuentes por semana
    sub_q = (
        select(
            func.date_trunc('week', Lista.FechaCreacion).label("semana"),
            Producto.IdProducto,
            Producto.Nombre,
            func.count().label("apariciones")
        )
        .join(ListaProducto, Lista.IdLista == ListaProducto.IdLista)
        .join(Producto, Producto.IdProducto == ListaProducto.IdProducto)
        .group_by("semana", Producto.IdProducto, Producto.Nombre)
    ).subquery()

    query5 = (
        select(
            sub_q.c.semana,
            sub_q.c.IdProducto,
            sub_q.c.Nombre,
            sub_q.c.apariciones
        )
        .order_by(sub_q.c.semana, desc(sub_q.c.apariciones))
    )
    result5 = await db.execute(query5)

    tendencias_semanales = {}
    for semana, id_prod, nombre_prod, apariciones in result5:
        key = semana.strftime("%Y-%m-%d")
        if key not in tendencias_semanales:
            tendencias_semanales[key] = []
        tendencias_semanales[key].append({
            "id_producto": id_prod,
            "producto": nombre_prod,
            "listas": apariciones
        })
    insights.append({"Tendencia semanal": tendencias_semanales})

    # Producto más comprado por categoría con distribución por proveedor
    query8 = (
        select(
            Categoria.NombreCategoria,
            Producto.IdProducto,
            Producto.Nombre,
            Proveedor.Nombre,
            func.count().label("Total")
        )
        .join(Producto, Categoria.IdCategoria == Producto.IdCategoria)
        .join(ListaProducto, Producto.IdProducto == ListaProducto.IdProducto)
        .join(Lista, Lista.IdLista == ListaProducto.IdLista)
        .join(Proveedor, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Categoria.NombreCategoria, Producto.IdProducto, Producto.Nombre, Proveedor.Nombre)
        .order_by(Categoria.NombreCategoria, desc("Total"))
    )
    result8 = await db.execute(query8)
    productos_categoria = {}
    for cat, id_prod, nombre_prod, proveedor, total in result8:
        if cat not in productos_categoria:
            productos_categoria[cat] = {
                "id_producto": id_prod,
                "producto": nombre_prod,
                "distribucion": []
            }
        if productos_categoria[cat]["producto"] == nombre_prod:
            productos_categoria[cat]["distribucion"].append({
                "proveedor": proveedor,
                "veces_comprado": total
            })
    insights.append({"Producto más comprado por categoría": productos_categoria})

    # Mapa de calor por hora del día (total representa la cantidad de listas creadas en esa hora)
    query9 = (
        select(extract('hour', Lista.FechaCreacion).label("hora"), func.count().label("total"))
        .group_by("hora")
        .order_by("hora")
    )
    result9 = await db.execute(query9)
    insights.append({"Mapa de calor por hora": [
        {"hora": int(r[0]), "total_listas_creadas": r[1]} for r in result9
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


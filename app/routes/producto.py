from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Producto, Categoria, UnidadMedida, Proveedor, ProductoProveedor, ListaProducto
from app.schemas.producto import ProductoCreate, ProductoResponse, ProductoUpdate, BigProductoProveedorResponse, ProductoConPrecioPromedioResponse, ProductoPrecioProveedorResponse
from sqlalchemy import select, func
from typing import List
from sqlalchemy.orm import joinedload
from app.schemas.productoproveedor import ProductoProveedorResponse
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, asc
from datetime import datetime
from sqlalchemy import delete  

from sqlalchemy import or_


router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nuevo producto


@router.post("/producto", response_model=ProductoResponse)
async def crear_producto(productoParam: ProductoCreate, db: Session = Depends(get_db)):
    # Verificar que la categoría existe
    categoria = await db.execute(select(Categoria).filter(Categoria.IdCategoria == productoParam.IdCategoria))
    categoria = categoria.scalars().first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría especificada no existe"
        )

    # Verificar que la unidad de medida existe
    unidad_medida = await db.execute(select(UnidadMedida).filter(UnidadMedida.IdUnidadMedida == productoParam.IdUnidadMedida))
    unidad_medida = unidad_medida.scalars().first()
    if not unidad_medida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La unidad de medida especificada no existe"
        )
    
    try:
        # Crear el nuevo producto
        nuevo_producto = Producto(
            IdCategoria = productoParam.IdCategoria,
            IdUnidadMedida = productoParam.IdUnidadMedida,
            Nombre = productoParam.Nombre,
            UrlImagen = productoParam.UrlImagen,
            Descripcion = productoParam.Descripcion,
            FechaCreacion=datetime.now().replace(tzinfo=None)
            
        )

        # Añadir el producto y realizar commit
        db.add(nuevo_producto)
        await db.commit()  # Usamos commit asincrónico
        await db.refresh(nuevo_producto)  # Refrescar para obtener el objeto actualizado

        return nuevo_producto

    except Exception as e:
        # Rollback en caso de error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al crear producto", "details": str(e)}
        )

# Obtener todos los productos   
@router.get("/producto", response_model=List[ProductoResponse])
async def obtener_productos(db: AsyncSession = Depends(get_db)):
    # Ejecutar la consulta asincrónica para obtener todos los productos
    result = await db.execute(select(Producto))
    productos = result.scalars().all()

    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    
    return productos

# Obtener todos los productos   
@router.get("/productoavg", response_model=List[ProductoConPrecioPromedioResponse])
async def obtener_productos(db: AsyncSession = Depends(get_db)):
    # Subconsulta: promedio de precios por producto
    subquery = (
        select(
            ProductoProveedor.IdProducto,
            func.avg(ProductoProveedor.Precio).label("precio_promedio")
        )
        .group_by(ProductoProveedor.IdProducto)
        .subquery()
    )

    # Consulta principal: unir Producto con promedio, ordenar por precio_promedio ascendente
    stmt = (
        select(
            Producto,
            subquery.c.precio_promedio
        )
        .outerjoin(subquery, Producto.IdProducto == subquery.c.IdProducto)
        .order_by(asc(subquery.c.precio_promedio))
    )

    result = await db.execute(stmt)
    filas = result.all()

    respuesta = []
    for producto, precio_promedio in filas:
        respuesta.append(ProductoConPrecioPromedioResponse(
            IdProducto=producto.IdProducto,
            IdCategoria=producto.IdCategoria,
            IdUnidadMedida=producto.IdUnidadMedida,
            Nombre=producto.Nombre,
            UrlImagen=producto.UrlImagen,
            Descripcion=producto.Descripcion,
            FechaCreacion=producto.FechaCreacion,
            PrecioPromedio=float(precio_promedio) if precio_promedio is not None else None
        ))

    return respuesta


# Obtener un producto por su id
@router.get("/producto/{id}", response_model=ProductoResponse)
async def obtener_producto_por_id(id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Obtener el producto asincrónicamente
        result = await db.execute(select(Producto).where(Producto.IdProducto == id))
        producto = result.scalar_one_or_none()

        if producto is None:
            raise HTTPException(status_code=404, detail="No existe el producto")

        return producto

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el producto: {str(e)}")


# Obtener productos por tipo de proveedor

@router.get("/productotipoproveedor/{id}", response_model=list[ProductoResponse])
async def obtener_productos_por_tipo_proveedor(
    id: int, db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Obtener IDs de proveedores que tienen ese tipo
        result_proveedores = await db.execute(
            select(Proveedor.IdProveedor).where(Proveedor.IdTipoProveedor == id)
        )
        ids_proveedores = result_proveedores.scalars().all()

        if not ids_proveedores:
            raise HTTPException(status_code=404, detail="No existen proveedores de ese tipo")

        # 2. Obtener los IDs de productos relacionados a esos proveedores
        result_productoproveedor = await db.execute(
            select(ProductoProveedor.IdProducto).where(
                ProductoProveedor.IdProveedor.in_(ids_proveedores)
            )
        )
        ids_productos = list(set(result_productoproveedor.scalars().all()))

        if not ids_productos:
            raise HTTPException(status_code=404, detail="No se encontraron productos asociados a esos proveedores")

        # 3. Obtener los productos
        result_productos = await db.execute(
            select(Producto).where(Producto.IdProducto.in_(ids_productos))
        )
        productos = result_productos.scalars().all()

        return productos

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Error al obtener los productos", "detalles": str(e)}
        )



# Actualizar un producto
@router.put("/producto/{id}", response_model=ProductoResponse)
async def actualizar_producto(
    id: int,
    productoParam: ProductoUpdate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Obtener producto existente de forma asincrónica
    result = await db.execute(select(Producto).where(Producto.IdProducto == id))
    producto = result.scalar_one_or_none()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Producto no encontrado", "id": id}
        )
    
    try:
        # 2. Obtener solo los campos proporcionados
        update_data = productoParam.model_dump(exclude_unset=True)
        
        # 3. Validaciones específicas asincrónicas
        if "IdCategoria" in update_data:
            result_categoria = await db.execute(select(Categoria).where(Categoria.IdCategoria == update_data["IdCategoria"]))
            if not result_categoria.scalar_one_or_none():
                raise ValueError("La categoría especificada no existe")
        
        if "IdUnidadMedida" in update_data:
            result_unidad = await db.execute(select(UnidadMedida).where(UnidadMedida.IdUnidadMedida == update_data["IdUnidadMedida"]))
            if not result_unidad.scalar_one_or_none():
                raise ValueError("La unidad de medida especificada no existe")
        
        # 4. Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(producto, field, value)
        
        await db.commit()
        await db.refresh(producto)
        return producto

    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "message": str(ve),
                "field": getattr(ve, 'field', None)
            }
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al actualizar producto",
                "details": str(e)
            }
        )

  
# Eliminar un producto
@router.delete("/producto/{id}", response_model=ProductoResponse)
async def eliminar_producto(id: int, db: AsyncSession = Depends(get_db)):
    # Buscar el producto
    result = await db.execute(select(Producto).where(Producto.IdProducto == id))
    producto = result.scalar_one_or_none()

    if producto is None:
        raise HTTPException(status_code=404, detail="No existe el producto")

    try:
        # 1. Eliminar relaciones con proveedores
        await db.execute(
            delete(ProductoProveedor).where(ProductoProveedor.IdProducto == id)
        )

        # 2. Eliminar relaciones en ListaProducto
        await db.execute(
            delete(ListaProducto).where(ListaProducto.IdProducto == id)
        )

        # 3. Eliminar el producto
        await db.delete(producto)

        # 4. Confirmar
        await db.commit()

        return producto

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al eliminar producto", "details": str(e)}
        )
    

# Obtener productos por categoria
@router.get("/productocategoria/{id}", response_model=List[ProductoResponse])
async def obtener_productos_por_categoria(id: int, db: AsyncSession = Depends(get_db)):
    # Realizar la consulta asincrónica para obtener los productos
    result = await db.execute(select(Producto).where(Producto.IdCategoria == id))
    productos = result.scalars().all()  # Obtener todos los productos de la categoría
    
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos para esta categoría")
    
    return productos

@router.get("/productotipoproveedor/{id}", response_model=list[ProductoResponse])
async def obtener_productos_por_tipo_proveedor(
    id: int, db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Obtener IDs de proveedores que tienen ese tipo
        result_proveedores = await db.execute(
            select(Proveedor.IdProveedor).where(Proveedor.IdTipoProveedor == id)
        )
        ids_proveedores = result_proveedores.scalars().all()

        if not ids_proveedores:
            raise HTTPException(status_code=404, detail="No existen proveedores de ese tipo")

        # 2. Obtener los IDs de productos relacionados a esos proveedores
        result_productoproveedor = await db.execute(
            select(ProductoProveedor.IdProducto).where(
                ProductoProveedor.IdProveedor.in_(ids_proveedores)
            )
        )
        ids_productos = list(set(result_productoproveedor.scalars().all()))

        if not ids_productos:
            raise HTTPException(status_code=404, detail="No se encontraron productos asociados a esos proveedores")

        # 3. Obtener los productos
        result_productos = await db.execute(
            select(Producto).where(Producto.IdProducto.in_(ids_productos))
        )
        productos = result_productos.scalars().all()

        return productos

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Error al obtener los productos", "detalles": str(e)}
        )



@router.get("/productosporproveedor/{id_proveedor}", response_model=list[ProductoResponse])
async def obtener_productos_por_proveedor(
    id_proveedor: int, db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Verificar si el proveedor existe
        proveedor = await db.scalar(
            select(Proveedor).where(Proveedor.IdProveedor == id_proveedor)
        )
        if not proveedor:
            raise HTTPException(
                status_code=404,
                detail={"error": "Proveedor no encontrado", "id_proveedor": id_proveedor}
            )

        # 2. Obtener IDs de productos asociados a ese proveedor
        result = await db.execute(
            select(Producto).join(ProductoProveedor).where(
                ProductoProveedor.IdProveedor == id_proveedor
            )
        )
        productos = result.scalars().all()

        if not productos:
            raise HTTPException(
                status_code=404,
                detail={"error": "Este proveedor no tiene productos asociados"}
            )

        return productos

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error al obtener productos por proveedor",
                "detalles": str(e)
            }
        )

#
@router.get("/precios-productos/proveedor/{id}", response_model=List[BigProductoProveedorResponse])
async def obtener_productos_con_precios(id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductoProveedor).options(joinedload(ProductoProveedor.Producto)).where(ProductoProveedor.IdProveedor == id)
    result = await db.execute(stmt)
    productos = result.scalars().all()
    return productos


@router.get("/precios-productos/{id_producto}", response_model=List[ProductoPrecioProveedorResponse])
async def obtener_precios_en_proveedores(id_producto: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ProductoProveedor)
        .options(joinedload(ProductoProveedor.Proveedor))
        .where(ProductoProveedor.IdProducto == id_producto)
    )

    result = await db.execute(stmt)
    productos_proveedor = result.scalars().all()

    if not productos_proveedor:
        raise HTTPException(status_code=404, detail="No hay precios para este producto en proveedores")

    respuesta = []
    for pp in productos_proveedor:
        respuesta.append(ProductoPrecioProveedorResponse(
            IdProveedor=pp.IdProveedor,
            NombreProveedor=pp.Proveedor.Nombre,     # nombre correcto
            UrlImagenProveedor=pp.Proveedor.UrlLogo, # URL logo correcto
            Precio=pp.Precio,
            PrecioOferta=pp.PrecioOferta,
            DescripcionOferta=pp.DescripcionOferta,
            FechaOferta=pp.FechaOferta,
            FechaPrecio=pp.FechaPrecio
        ))
    
    return respuesta

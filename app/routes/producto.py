from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Producto, Categoria, UnidadMedida, Proveedor, ProductoProveedor
from app.schemas.producto import ProductoCreate, ProductoResponse, ProductoUpdate
from app.schemas.productoproveedor import ProductoProveedorResponse
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
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
            NombreProducto = productoParam.Nombre,
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
async def actualizar_producto(id: int, productoParam: ProductoUpdate, db: Session = Depends(get_db)):
    # 1. Obtener producto existente
    producto = db.query(Producto).filter(Producto.IdProducto == id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Producto no encontrado", "id": id}
        )
    
    try:
        # 2. Obtener solo los campos proporcionados
        update_data = productoParam.model_dump(exclude_unset=True)
        
        # 3. Validaciones específicas
        if "IdCategoria" in update_data:
            if not db.query(Categoria).get(update_data["IdCategoria"]):
                raise ValueError("La categoría especificada no existe")
        
        if "IdUnidadMedida" in update_data:
            if not db.query(UnidadMedida).get(update_data["IdUnidadMedida"]):
                raise ValueError("La unidad de medida especificada no existe")
        
        
        # 4. Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(producto, field, value)
        
        db.commit()
        db.refresh(producto)
        return producto
        
    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "message": str(ve),
                "field": ve.field if hasattr(ve, 'field') else None
            }
        )
    except Exception as e:
        db.rollback()
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
    # Obtener el producto por id
    result = await db.execute(select(Producto).where(Producto.IdProducto == id))
    producto = result.scalar_one_or_none()

    if producto is None:
        raise HTTPException(status_code=404, detail="No existe el producto")

    try:
        # Eliminar el producto
        await db.delete(producto)
        await db.commit()
    
        return producto  # Devuelve el producto antes de eliminarlo

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
        result_proveedor = await db.execute(
            select(Proveedor).where(Proveedor.IdProveedor == id_proveedor)
        )
        proveedor = result_proveedor.scalar_one_or_none()

        if not proveedor:
            raise HTTPException(
                status_code=404,
                detail={"error": "Proveedor no encontrado", "id_proveedor": id_proveedor}
            )

        # 2. Obtener IDs de productos asociados a ese proveedor
        result_relaciones = await db.execute(
            select(ProductoProveedor.IdProducto).where(
                ProductoProveedor.IdProveedor == id_proveedor
            )
        )
        ids_productos = result_relaciones.scalars().all()

        if not ids_productos:
            raise HTTPException(
                status_code=404,
                detail={"error": "Este proveedor no tiene productos asociados"}
            )

        # 3. Obtener los productos
        result_productos = await db.execute(
            select(Producto).where(Producto.IdProducto.in_(ids_productos))
        )
        productos = result_productos.scalars().all()

        return productos

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error al obtener productos por proveedor",
                "detalles": str(e)
            }
        )


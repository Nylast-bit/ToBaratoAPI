from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import ProductoProveedor, Producto, Proveedor
from app.schemas.productoproveedor import ProductoProveedorCreate, ProductoProveedorResponse, ProductoProveedorUpdate
from app.database import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/productoproveedor", response_model=ProductoProveedorResponse)
async def crear_listaproducto(
    productoproveedorParam: ProductoProveedorCreate, 
    db: AsyncSession = Depends(get_db)
):
    # 1. Validar que el producto exista
    result_producto = await db.execute(
        select(Producto).where(Producto.IdProducto == productoproveedorParam.IdProducto)
    )
    producto = result_producto.scalar_one_or_none()
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    # 2. Validar que el proveedor exista
    result_proveedor = await db.execute(
        select(Proveedor).where(Proveedor.IdProveedor == productoproveedorParam.IdProveedor)
    )
    proveedor = result_proveedor.scalar_one_or_none()
    if not proveedor:
        raise HTTPException(
            status_code=404,
            detail="Proveedor no encontrado"
        )

    # 3. Crear el nuevo producto proveedor
    nuevo_productoproveedor = ProductoProveedor(
        IdProducto=productoproveedorParam.IdProducto,
        IdProveedor=productoproveedorParam.IdProveedor,
        Precio=productoproveedorParam.Precio,
        PrecioOferta=productoproveedorParam.PrecioOferta,
        DescripcionOferta=productoproveedorParam.DescripcionOferta,
        FechaOferta=productoproveedorParam.FechaOferta,
        FechaPrecio=productoproveedorParam.FechaPrecio,
    )

    # 4. Guardar en la base de datos
    db.add(nuevo_productoproveedor)
    await db.commit()
    await db.refresh(nuevo_productoproveedor)

    # 5. Retornar el nuevo registro
    return nuevo_productoproveedor


# Obtener todos los productos
@router.get("/productoproveedor", response_model=List[ProductoProveedorResponse])
async def obtener_productoproveedor(db: AsyncSession = Depends(get_db)):
    # 1. Ejecutar la consulta asincrónica
    result = await db.execute(select(ProductoProveedor))
    productoproveedor = result.scalars().all()

    # 2. Validar si no se encontraron registros
    if not productoproveedor:
        raise HTTPException(status_code=404, detail="No se encontraron productos")

    # 3. Retornar los resultados
    return productoproveedor



# Obtener un productoproveedor por ID    
@router.get("/productos/{id_producto}/proveedores/{id_proveedor}", response_model=ProductoProveedorResponse)
async def obtener_productoproveedor_por_id(id_producto: int, id_proveedor: int, db: AsyncSession = Depends(get_db)):
    # 1. Ejecutar la consulta asincrónica
    result = await db.execute(
        select(ProductoProveedor).filter(
            ProductoProveedor.IdProducto == id_producto,
            ProductoProveedor.IdProveedor == id_proveedor
        )
    )
    productoproveedor = result.scalar_one_or_none()

    # 2. Verificar si no se encontró el producto proveedor
    if not productoproveedor:
        raise HTTPException(status_code=404, detail="No se encontraron productos")

    # 3. Retornar el resultado
    return productoproveedor


#actualizar un productoproveedor
@router.put("/productos/{id_producto}/proveedores/{id_proveedor}", response_model=ProductoProveedorResponse)
async def actualizar_producto_proveedor(
    id_producto: int,
    id_proveedor: int,
    datos: ProductoProveedorUpdate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Validar que el producto exista
    result_producto = await db.execute(
        select(Producto).where(Producto.IdProducto == id_producto)
    )
    producto = result_producto.scalar_one_or_none()
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    # 2. Validar que el proveedor exista
    result_proveedor = await db.execute(
        select(Proveedor).where(Proveedor.IdProveedor == id_proveedor)
    )
    proveedor = result_proveedor.scalar_one_or_none()
    if not proveedor:
        raise HTTPException(
            status_code=404,
            detail="Proveedor no encontrado"
        )

    # 3. Buscar la relación entre producto y proveedor
    relacion = await db.execute(
        select(ProductoProveedor).where(
            ProductoProveedor.IdProducto == id_producto,
            ProductoProveedor.IdProveedor == id_proveedor
        )
    )
    relacion = relacion.scalar_one_or_none()

    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Relación entre producto y proveedor no encontrada"
        )

    try:
        # 4. Validar y procesar datos
        update_data = datos.model_dump(exclude_unset=True)

        for campo, valor in update_data.items():
            setattr(relacion, campo, valor)

        # 5. Aplicar la actualización
        await db.commit()
        await db.refresh(relacion)
        return relacion

    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

#Eliminar un producto de un proveedor
@router.delete(
    "/productos/{id_producto}/proveedores/{id_proveedor}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar relación Producto-Proveedor",
    description="Elimina la asociación entre un producto y un proveedor específicos y devuelve el producto y proveedor eliminados"
)
async def eliminar_producto_proveedor(
    id_producto: int,
    id_proveedor: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina una relación Producto-Proveedor por sus IDs compuestos
    
    - **id_producto**: ID del producto (entero)
    - **id_proveedor**: ID del proveedor (entero)
    """
    # Buscar la relación existente
    result = await db.execute(
        select(ProductoProveedor).where(
            ProductoProveedor.IdProducto == id_producto,
            ProductoProveedor.IdProveedor == id_proveedor
        )
    )
    relacion = result.scalar_one_or_none()
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "detalle": f"No existe relación entre Producto ID {id_producto} y Proveedor ID {id_proveedor}",
                "solucion": "Verifique los IDs proporcionados"
            }
        )
    
    try:
        # Obtener los datos del Producto y Proveedor asociados a la relación
        producto = await db.execute(select(Producto).where(Producto.IdProducto == id_producto))
        proveedor = await db.execute(select(Proveedor).where(Proveedor.IdProveedor == id_proveedor))

        producto = producto.scalar_one_or_none()
        proveedor = proveedor.scalar_one_or_none()

        if not producto or not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto o Proveedor no encontrado"
            )

        # Eliminar la relación
        await db.delete(relacion)
        await db.commit()

        # Retornar la información del Producto y Proveedor eliminados
        return {
            "relacion_eliminada": relacion
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al eliminar relación",
                "detalle": str(e),
                "solucion": "Intente nuevamente o contacte al administrador"
            }
        )

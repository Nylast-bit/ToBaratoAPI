from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import ProductoProveedor
from app.schemas.productoproveedor import ProductoProveedorCreate, ProductoProveedorResponse, ProductoProveedorUpdate
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
@router.post("/productoproveedor", response_model=ProductoProveedorResponse)
async def crear_listaproducto(productoproveedorParam: ProductoProveedorCreate, db: Session = Depends(get_db)):
    nuevo_productoproveedor= ProductoProveedor(
        IdProducto = productoproveedorParam.IdProveedor, # ← Usa el nombre correcto
        IdProveedor = productoproveedorParam.IdProveedor, # ← Usa el nombre correcto
        Precio = productoproveedorParam.Precio, # ← Usa el nombre correcto
        PrecioOferta = productoproveedorParam.PrecioOferta, # ← Usa el nombre correcto
        DescripcionOferta = productoproveedorParam.DescripcionOferta, # ← Usa el nombre correcto
        FechaOferta = productoproveedorParam.FechaOferta, # ← Usa el nombre correcto
        FechaPrecio = productoproveedorParam.FechaPrecio, # ← Usa el nombre correcto

    )
    db.add(nuevo_productoproveedor)
    db.commit()
    db.refresh(nuevo_productoproveedor)
    return nuevo_productoproveedor


# Obtener todos los productos
@router.get("/productoproveedor", response_model=List[ProductoProveedorResponse])
async def obtener_productoproveedor(db: Session = Depends(get_db)):
    productoproveedor = db.query(ProductoProveedor).all()
    if not productoproveedor:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productoproveedor


# Obtener un productoproveedor por ID    
@router.get("/productos/{id_producto}/proveedores/{id_proveedor}", response_model=ProductoProveedorResponse)
async def obtener_productoproveedor_por_id(id_producto: int, id_proveedor: int, db: Session = Depends(get_db)):
    productoproveedor = db.query(ProductoProveedor).filter(
        ProductoProveedor.IdProducto == id_producto,
        ProductoProveedor.IdProveedor == id_proveedor
    ).first()
    if not productoproveedor:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productoproveedor

#actualizar un productoproveedor
@router.put("/productos/{id_producto}/proveedores/{id_proveedor}", response_model=ProductoProveedorResponse)
async def actualizar_producto_proveedor(
    id_producto: int,
    id_proveedor: int,
    datos: ProductoProveedorUpdate,
    db: Session = Depends(get_db)
):
    relacion = db.query(ProductoProveedor).filter(
        ProductoProveedor.IdProducto == id_producto,
        ProductoProveedor.IdProveedor == id_proveedor
    ).first()
    
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Relación no encontrada",
                "IdProducto": id_producto,
                "IdProveedor": id_proveedor
            }
        )
    
    try:
        update_data = datos.model_dump(exclude_unset=True)
        
        
        for campo, valor in update_data.items():
            setattr(relacion, campo, valor)
        
        db.commit()
        db.refresh(relacion)
        return relacion
    
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    

#Eliminar un producto proveedor
@router.delete(
    "/productos/{id_producto}/proveedores/{id_proveedor}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar relación Producto-Proveedor",
    description="Elimina la asociación entre un producto y un proveedor específicos"
)
async def eliminar_producto_proveedor(
    id_producto: int,
    id_proveedor: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una relación Producto-Proveedor por sus IDs compuestos
    
    - **id_producto**: ID del producto (entero)
    - **id_proveedor**: ID del proveedor (entero)
    """
    # Buscar la relación existente
    relacion = db.query(ProductoProveedor).filter(
        ProductoProveedor.IdProducto == id_producto,
        ProductoProveedor.IdProveedor == id_proveedor
    ).first()
    
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
        db.delete(relacion)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al eliminar relación",
                "detalle": str(e),
                "solucion": "Intente nuevamente o contacte al administrador"
            }
        )
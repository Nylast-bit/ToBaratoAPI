from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Producto, Categoria, UnidadMedida
from app.schemas.producto import ProductoCreate, ProductoResponse, ProductoUpdate
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
@router.post("/producto", response_model=ProductoResponse)
async def crear_producto(productoParam: ProductoCreate, db: Session = Depends(get_db)):
    nuevo_producto = Producto(
        IdCategoria = productoParam.IdCategoria, # ← Usa el nombre correcto
        IdUnidadMedida = productoParam.IdUnidadMedida, # ← Usa el nombre correcto
        Nombre = productoParam.Nombre, # ← Usa el nombre correcto
        UrlImagen = productoParam.UrlImagen, # ← Usa el nombre correcto
        Descripcion = productoParam.Descripcion # ← Usa el nombre correcto
    )
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto


# Obtener todos los productos   
@router.get("/producto", response_model=List[ProductoResponse])
async def obtener_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productos

# Obtener un producto por su id
@router.get("/producto/{id}", response_model=ProductoResponse)
async def obtener_producto_por_id(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.IdProducto == id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="No existe el producto")
    return producto

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
async def eliminar_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.IdProducto == id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="No existe el producto")

    db.delete(producto)
    db.commit()
    
    return producto  # ← Devuelve el objeto antes de eliminarlo en la sesión
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Categoria, Producto
from app.schemas.categoria import CategoriaCreate, CategoriaResponse
from app.database import AsyncSessionLocal
from sqlalchemy import select, delete
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#Crear una nueva categoria
@router.post("/categoria", response_model=CategoriaResponse)
async def crear_categoria(
    categoriaParams: CategoriaCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        nombre_limpio = categoriaParams.NombreCategoria.strip()

        # Validaciones básicas
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacío")
        if nombre_limpio.isdigit():
            raise ValueError("El nombre no puede ser solo números")

        nueva_categoria = Categoria(
            NombreCategoria=nombre_limpio.title(),
            FechaCreacion=datetime.now().replace(tzinfo=None)  # <-- quita la zona horaria
        )

        db.add(nueva_categoria)
        await db.commit()
        await db.refresh(nueva_categoria)
        return nueva_categoria

    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Error de validación",
                "message": str(ve),
                "field": "NombreCategoria",
                "value": categoriaParams.NombreCategoria
            }
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error interno",
                "message": str(e)
            }
        )



#Obtener todas las categorias
@router.get("/categoria", response_model=List[CategoriaResponse])
async def obtener_categorias(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Categoria))
        categorias = result.scalars().all()
        return categorias


#Obtener una categoria por su id
@router.get("/categoria/{id}", response_model=CategoriaResponse)
async def obtener_categoria_por_id(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(
            select(Categoria).where(Categoria.IdCategoria == id)
        )
        categoria = result.scalars().first()
        
        if categoria is None:
            raise HTTPException(
                status_code=404, 
                detail="No existe el tipo de categoria"
            )
        return categoria


#Actualizar unacategoria
@router.put("/categoria/{id}", response_model=CategoriaResponse)
async def actualizar_categoria(
    id: int,
    categoriaParams: CategoriaCreate,
    db: AsyncSession = Depends(get_db)
):
    async with db as session:
        result = await session.execute(
            select(Categoria).where(Categoria.IdCategoria == id)
        )
        categoria = result.scalars().first()

        if categoria is None:
            raise HTTPException(status_code=404, detail="No existe el tipo de categoria")
        
        categoria.NombreCategoria = categoriaParams.NombreCategoria.strip().title()

        await session.commit()
        await session.refresh(categoria)

        return categoria


#Eliminar una categoria
@router.delete("/categoria/{id}", response_model=CategoriaResponse)
async def eliminar_categoria(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        # Buscar la categoría
        result = await session.execute(
            select(Categoria).where(Categoria.IdCategoria == id)
        )
        categoria = result.scalars().first()

        if categoria is None:
            raise HTTPException(status_code=404, detail="No existe la categoría")

        # Verificar si hay productos relacionados con esta categoría
        result_productos = await session.execute(
            select(Producto).where(Producto.IdCategoria == id)
        )
        productos_relacionados = result_productos.scalars().all()

        if productos_relacionados:
            # Eliminar todos los productos asociados a esta categoría
            await session.execute(
                delete(Producto).where(Producto.IdCategoria == id)
            )

        # Eliminar la categoría
        await session.delete(categoria)
        await session.commit()

        return categoria


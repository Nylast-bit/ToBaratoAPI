from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaResponse
from app.database import AsyncSessionLocal



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
async def crear_categoria(categoriaParams: CategoriaCreate, db: Session = Depends(get_db)):
    nuevo_tipo = Categoria(
        NombreCategoria=categoriaParams.NombreCategoria  # ← Usa el nombre correcto
    )
    db.add(nuevo_tipo)
    db.commit()
    db.refresh(nuevo_tipo)
    return nuevo_tipo


#Obtener todas las categorias
@router.get("/categoria", response_model=List[CategoriaResponse])
async def obtener_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return categorias

#Obtener una categoria por su id
@router.get("/categoria/{id}", response_model=CategoriaResponse)
async def obtener_categorias_por_id(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.IdCategoria == id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de categoria")
    return categoria

#Actualizar unacategoria
@router.put("/categoria/{id}", response_model=CategoriaResponse)
async def actualizar_categoria(id: int, categoriaParams: CategoriaCreate, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.IdCategoria == id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de categoria")
    categoria.NombreCategoria = categoriaParams.NombreCategoria  # ← Usa el nombre correcto
    db.commit()
    db.refresh(categoria)
    return categoria

#Eliminar una categoria
@router.delete("/categoria/{id}", response_model=CategoriaResponse)
async def eliminar_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.IdCategoria == id).first()
    if categoria is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de categoria")

    db.delete(categoria)
    db.commit()
    
    return categoria  # ← Devuelve el objeto antes de eliminarlo en la sesión

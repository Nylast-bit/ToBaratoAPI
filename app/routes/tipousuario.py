from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import TipoUsuario
from app.schemas.tipousuario import TipoUsuarioCreate, TipoUsuarioResponse
from app.database import AsyncSessionLocal
from fastapi import HTTPException, status
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



@router.post("/tipousuario", response_model=TipoUsuarioResponse)
async def crear_tipo_usuario(
    tipo_data: TipoUsuarioCreate,  # Usa el modelo corregido
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validaciones
        nombre_limpio = tipo_data.NombreTipoUsuario.strip()  # Accede al campo correcto
        
        if nombre_limpio.isdigit():
            raise ValueError("El nombre no puede ser numérico")
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacío")

        

        # Crear nuevo registro
        nuevo_tipo = TipoUsuario(
            NombreTipoUsuario=nombre_limpio.title()  # Usa el nombre de campo de SQLAlchemy
        )
        
        db.add(nuevo_tipo)
        await db.commit()
        await db.refresh(nuevo_tipo)
        return nuevo_tipo
        
    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Error de validación",
                "message": str(ve),
                "field": "nombre",
                "value": nombre_limpio
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

#Obtener todos los tipos de usuarios
@router.get("/tipousuario", response_model=List[TipoUsuarioResponse])
async def obtener_tipos_usuario(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(TipoUsuario))
        tipos_usuario = result.scalars().all()
        return tipos_usuario

#Obtener un tipo de usuario por su id
@router.get("/tipousuario/{id}", response_model=TipoUsuarioResponse)
async def obtener_tipo_usuario_por_id(id: int, db: AsyncSession = Depends(get_db)):
    # Execute async query
    result = await db.execute(
        select(TipoUsuario).where(TipoUsuario.IdTipoUsuario == id)
    )
    tipo_usuario = result.scalars().first()
    
    if tipo_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe el tipo de usuario"
        )
    return tipo_usuario

#Actualizar un tipo de usuario
@router.put("/tipousuario/{id}", response_model=TipoUsuarioResponse)
async def actualizar_tipo_usuario(id: int, tipoUsuarioParam: TipoUsuarioCreate, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(TipoUsuario).where(TipoUsuario.IdTipoUsuario == id))
        tipousuario = result.scalars().first()
        if tipousuario is None:
            raise HTTPException(status_code=404, detail="No existe el tipo de usuario")
        
        tipousuario.NombreTipoUsuario = tipoUsuarioParam.NombreTipoUsuario
        
        await session.commit()
        await session.refresh(tipousuario)
        return tipousuario

#Eliminar un tipo de usuario
@router.delete("/tipousuario/{id}", response_model=TipoUsuarioResponse)
async def eliminar_tipo_usuario(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(TipoUsuario).where(TipoUsuario.IdTipoUsuario == id))
        tipo_usuario = result.scalars().first()
        if tipo_usuario is None:
            raise HTTPException(status_code=404, detail="No existe el tipo de usuario")

        await session.delete(tipo_usuario)
        await session.commit()

        return tipo_usuario
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import UnidadMedida
from app.schemas.unidadmedida import UnidadMedidaCreate, UnidadMedidaResponse
from app.database import AsyncSessionLocal
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime



router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
       await db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#Crear un nueva unidad de medida
@router.post("/unidadmedida", response_model=UnidadMedidaResponse)
async def crear_unidadmedida(
    unidadMedidaParam: UnidadMedidaCreate, 
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validaciones
        nombre_limpio = unidadMedidaParam.NombreUnidadMedida.strip()

        if nombre_limpio.isdigit():
            raise ValueError("El nombre no puede ser numérico")
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacío")

        # Crear nuevo registro
        nueva_unidad = UnidadMedida(
            NombreUnidadMedida=nombre_limpio.title(),
            FechaCreacion=datetime.now().replace(tzinfo=None)  # <-- quita la zona horaria
                # Usa el nombre de campo correcto
        )

        # Guardar en la base de datos
        db.add(nueva_unidad)
        await db.commit()
        await db.refresh(nueva_unidad)

        return nueva_unidad
        
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



#Obtener todas las unidades de medida
@router.get("/unidadmedida", response_model=List[UnidadMedidaResponse])
async def obtener_unidadmedida(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(UnidadMedida))
        unidadmedida = result.scalars().all()
        return unidadmedida


#Obtener una unidad de medida por su id
@router.get("/unidadmedida/{id}", response_model=UnidadMedidaResponse)
async def obtener_unidadmedida_por_id(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(UnidadMedida).where(UnidadMedida.IdUnidadMedida == id))
        unidadmedida = result.scalars().first()

        if unidadmedida is None:
            raise HTTPException(status_code=404, detail="No existe esa unidad de medida")

        return unidadmedida


#Actualizar una unidad de medida
@router.put("/unidadmedida/{id}", response_model=UnidadMedidaResponse)
async def actualizar_unidadmedida(id: int, unidadmMedidaParam: UnidadMedidaCreate, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(UnidadMedida).where(UnidadMedida.IdUnidadMedida == id))
        unidadmedida = result.scalars().first()

        if unidadmedida is None:
            raise HTTPException(status_code=404, detail="No existe esa unidad de medida")

        unidadmedida.NombreUnidadMedida = unidadmMedidaParam.NombreUnidadMedida  # ← Usa el nombre correcto
        
        await session.commit()
        await session.refresh(unidadmedida)

        return unidadmedida


#Eliminar una unidad de medida
@router.delete("/unidadmedida/{id}", response_model=UnidadMedidaResponse)
async def eliminar_unidadmedida(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(UnidadMedida).where(UnidadMedida.IdUnidadMedida == id))
        unidadmedida = result.scalars().first()

        if unidadmedida is None:
            raise HTTPException(status_code=404, detail="No existe esa unidad de medida")

        await session.delete(unidadmedida)  # Eliminar de forma asincrónica
        await session.commit()  # Operación asincrónica
        
        return unidadmedida  # Devuelve el objeto antes de eliminarlo en la sesión


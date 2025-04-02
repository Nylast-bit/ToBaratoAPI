from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import UnidadMedida
from app.database import SessionLocal
from app.schemas.unidadmedida import UnidadMedidaCreate, UnidadMedidaResponse


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#Crear un nueva unidad de medida
@router.post("/unidadmedida", response_model=UnidadMedidaResponse)
def crear_unidadmedida(unidadmMedidaParam: UnidadMedidaCreate, db: Session = Depends(get_db)):
    nuevo_tipo = UnidadMedida(
        NombreUnidadMedida = unidadmMedidaParam.NombreUnidadMedida # ← Usa el nombre correcto
    )
    db.add(nuevo_tipo)
    db.commit()
    db.refresh(nuevo_tipo)
    return nuevo_tipo


#Obtener todas las unidades de medida
@router.get("/unidadmedida", response_model=List[UnidadMedidaResponse])
def obtener_unidadmedida(db: Session = Depends(get_db)):
    unidadmedida = db.query(UnidadMedida).all()
    return unidadmedida

#Obtener una unidad de medida por su id
@router.get("/unidadmedida/{id}", response_model=UnidadMedidaResponse)
def obtener_unidadmedida_por_id(id: int, db: Session = Depends(get_db)):
    unidadmedida = db.query(UnidadMedida).filter(UnidadMedida.IdUnidadMedida == id).first()
    if unidadmedida is None:
        raise HTTPException(status_code=404, detail="No existe esa unidad de medida")
    return unidadmedida

#Actualizar una unidad de medida
@router.put("/unidadmedida/{id}", response_model=UnidadMedidaResponse)
def actualizar_unidadmedida(id: int, unidadmMedidaParam: UnidadMedidaCreate, db: Session = Depends(get_db)):
    unidadmedida = db.query(UnidadMedida).filter(UnidadMedida.IdUnidadMedida == id).first()
    if unidadmedida is None:
        raise HTTPException(status_code=404, detail="No existe esa unidad de medida")
    unidadmedida.NombreUnidadMedida = unidadmMedidaParam.NombreUnidadMedida  # ← Usa el nombre correcto
    db.commit()
    db.refresh(unidadmedida)
    return unidadmedida

#Eliminar una unidad de medida
@router.delete("/unidadmedida/{id}", response_model=UnidadMedidaResponse)
def eliminar_unidadmedida(id: int, db: Session = Depends(get_db)):
    unidadmedida = db.query(UnidadMedida).filter(UnidadMedida.IdUnidadMedida == id).first()
    if unidadmedida is None:
        raise HTTPException(status_code=404, detail="No existe esa unidad de medida")

    db.delete(unidadmedida)
    db.commit()
    
    return unidadmedida  # ← Devuelve el objeto antes de eliminarlo en la sesión

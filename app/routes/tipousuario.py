from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import TipoUsuario
from app.database import SessionLocal
from app.schemas.tipousuario import TipoUsuarioCreate, TipoUsuarioResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


#Crear un nuevo tipo de usuario
@router.post("/tipousuario", response_model=TipoUsuarioResponse)
def crear_tipo_usuario(tipoUsuarioParam: TipoUsuarioCreate, db: Session = Depends(get_db)):
    try:
        # Validar que el nombre no sea numérico
        if tipoUsuarioParam.NombreTipoUsuario.isdigit():
            raise ValueError("El nombre no puede ser un valor numérico")
        
        # Validar que no esté vacío
        if not tipoUsuarioParam.NombreTipoUsuario.strip():
            raise ValueError("El nombre no puede estar vacío")
        
        nuevo_tipo = TipoUsuario(
            NombreTipoUsuario=tipoUsuarioParam.NombreTipoUsuario.strip().title()  # Limpieza básica
        )
        
        db.add(nuevo_tipo)
        db.commit()
        db.refresh(nuevo_tipo)
        return nuevo_tipo
        
    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "message": str(ve),
                "field": "NombreTipoUsuario",
                "received_value": tipoUsuarioParam.NombreTipoUsuario
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error interno al crear tipo de usuario",
                "message": str(e)
            }
        )


#Obtener todos los tipos de usuarioss
@router.get("/tipousuario", response_model=List[TipoUsuarioResponse])
def obtener_tipos_usuario(db: Session = Depends(get_db)):
    tipos_usuario = db.query(TipoUsuario).all()
    return tipos_usuario

#Obtener un tipo de usuario por su id
@router.get("/tipousuario/{id}", response_model=TipoUsuarioResponse)
def obtener_tipo_usuario_por_id(id: int, db: Session = Depends(get_db)):
    tipo_usuario = db.query(TipoUsuario).filter(TipoUsuario.IdTipoUsuario == id).first()
    if tipo_usuario is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de usuario")
    return tipo_usuario

#Actualizar un tipo de usuario
@router.put("/tipousuario/{id}", response_model=TipoUsuarioResponse)
def actualizar_tipo_usuario(id: int, tipoUsuarioParam: TipoUsuarioCreate, db: Session = Depends(get_db)):
    tipousuario = db.query(TipoUsuario).filter(TipoUsuario.IdTipoUsuario == id).first()
    if tipousuario is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de usuario")
    tipousuario.NombreTipoUsuario = tipoUsuarioParam.NombreTipoUsuario  # ← Usa el nombre correcto
    db.commit()
    db.refresh(tipousuario)
    return tipousuario

#Eliminar un tipo de usuario
@router.delete("/tipousuario/{id}", response_model=TipoUsuarioResponse)
def eliminar_tipo_usuario(id: int, db: Session = Depends(get_db)):
    tipo_usuario = db.query(TipoUsuario).filter(TipoUsuario.IdTipoUsuario == id).first()
    if tipo_usuario is None:
        raise HTTPException(status_code=404, detail="No existe el tipo de usuario")

    db.delete(tipo_usuario)
    db.commit()
    
    return tipo_usuario  # ← Devuelve el objeto antes de eliminarlo en la sesión

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Usuario, TipoUsuario
from app.database import SessionLocal
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from passlib.context import CryptContext


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/usuario", response_model=UsuarioResponse)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el correo ya existe
    if db.query(Usuario).filter(Usuario.Correo == usuario.Correo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "El correo ya está registrado",
                "code": "EMAIL_ALREADY_EXISTS",
                "field": "Correo",
                "value": usuario.Correo
            }
        )
    
    # Verificar tipo de usuario
    if not db.query(TipoUsuario).get(usuario.IdTipoUsuario):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Tipo de usuario no válido",
                "code": "INVALID_USER_TYPE",
                "field": "IdTipoUsuario",
                "value": usuario.IdTipoUsuario
            }
        )
    
    try:
        nuevo_usuario = Usuario(
            IdTipoUsuario=usuario.IdTipoUsuario,
            NombreUsuario=usuario.NombreUsuario,
            Correo=usuario.Correo,
            Telefono=usuario.Telefono,
            Clave=hash_password(usuario.Clave),  # Asegúrate de hashear la contraseña
            Nombres=usuario.Nombres,
            Apellidos=usuario.Apellidos,
            Estado=usuario.Estado,
            FechaNacimiento=usuario.FechaNacimiento,
            UrlPerfil=usuario.UrlPerfil,

        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al crear usuario",
                "code": "USER_CREATION_ERROR",
                "details": str(e)
            }
        )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#Obtener todos los usuarios
@router.get("/usuario", response_model=List[UsuarioResponse])
def obtener_usuario(db: Session = Depends(get_db)):
    usuario = db.query(Usuario).all()
    return usuario

#Obtener un usuario por su id
@router.get("/usuario/{id}", response_model=UsuarioResponse)
def obtener_unidadmedida_por_id(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.IdUsuario == id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="No existe esa unidad de medida")
    return usuario


#Actualizar una unidad de medida
@router.put("/usuario/{id}", response_model=UsuarioResponse)
def actualizar_unidadmedida(id: int, usuarioParam: UsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.IdUsuario == id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="No existe esa unidad de medida")
    IdTipoUsuario=usuario.IdTipoUsuario,
    NombreUsuario=usuario.NombreUsuario,
    Correo=usuario.Correo,
    Telefono=usuario.Telefono,
    Clave=hash_password(usuario.Clave),  # Asegúrate de hashear la contraseña
    Nombres=usuario.Nombres,
    Apellidos=usuario.Apellidos,
    Estado=usuario.Estado,
    FechaNacimiento=usuario.FechaNacimiento,
    UrlPerfil=usuario.UrlPerfil,  # ← Usa el nombre correcto
    db.commit()
    db.refresh(usuario)
    return usuario


#Hashar la contraseña
def hash_password(password: str):
    return pwd_context.hash(password)



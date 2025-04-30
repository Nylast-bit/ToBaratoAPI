from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Usuario, TipoUsuario
from app.database import SessionLocal
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate, UsuarioUpdatePassword
from passlib.context import CryptContext
import bcrypt


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/login", response_model=UsuarioResponse)


@router.post("/signup", response_model=UsuarioResponse)
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


#Actualizar un usuario
@router.put("/usuario/{id}", response_model=UsuarioResponse)
def actualizar_usuario(id: int, usuarioParam: UsuarioUpdate, db: Session = Depends(get_db)):
    # 1. Obtener usuario existente
    usuario = db.query(Usuario).filter(Usuario.IdUsuario == id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Usuario no encontrado", "id": id}
        )
    
    try:
        # 2. Obtener solo los campos proporcionados (ignorar None)
        update_data = usuarioParam.model_dump(exclude_unset=True)
        
        
        if "Correo" in update_data:
            # Validar que el correo no esté en uso por otro usuario
            if db.query(Usuario).filter(
                Usuario.Correo == update_data["Correo"],
                Usuario.IdUsuario != id
            ).first():
                raise ValueError("El correo ya está registrado por otro usuario")
        
        if "Telefono" in update_data:
            # Validar formato de teléfono
            if not update_data["Telefono"].isdigit():
                raise ValueError("El teléfono debe contener solo números")
        
        # 4. Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(usuario, field, value)
        
        db.commit()
        db.refresh(usuario)
        return usuario
        
    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error de validación", "message": str(ve)}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar usuario", "details": str(e)}
        )


#Eliminar un usuario
@router.delete("/usuario/{id}", response_model=UsuarioResponse)
def eliminar_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.IdUsuario == id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="No existe ese usuario")

    db.delete(usuario)
    db.commit()
    
    return usuario  # ← Devuelve el objeto antes de eliminarlo en la sesión

@router.put("/change-password", response_model=UsuarioResponse)
def cambiar_contraseña(datos: UsuarioUpdatePassword, db: Session = Depends(get_db)):
    # Buscar al usuario
    usuario_db = db.query(Usuario).filter(Usuario.IdUsuario == datos.IdUsuario).first()
    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Usuario no encontrado", "id": datos.IdUsuario}
        )

    # Verificar la clave actual
    if not verify_password(datos.Clave, usuario_db.Clave):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "La clave actual no es correcta"}
        )

    # Actualizar la contraseña
    try:
        usuario_db.Clave = hash_password(datos.ClaveNueva)
        db.commit()
        db.refresh(usuario_db)
        return {"message": "Usuario actualizado con éxito"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar usuario", "details": str(e)}
        )
    
        
       

#Hashar la contraseña
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Lo guardas como string en la DB


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


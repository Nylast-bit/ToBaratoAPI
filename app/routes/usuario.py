from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Usuario, TipoUsuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate, UsuarioUpdatePassword, UsuarioLoginModel, LoginResponseModel, TokenModel, UsuarioResponseModel
import bcrypt
from app.auth.utils import createAccessToken, decodeAccessToken
from app.auth.service import UsuarioService
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime
from app.dependencies import get_session
from app.database import AsyncSessionLocal
from app.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from fastapi.responses import JSONResponse

import re
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()
REFRESH_TOKEN_EXPIRY = 3600 
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]



from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

@router.post("/signup", response_model=UsuarioResponse)
async def crear_usuario(usuario: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    # 1. Verificar si el correo ya existe (forma asíncrona)
    result = await db.execute(
        select(Usuario).where(Usuario.Correo == usuario.Correo)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "El correo ya está registrado",
                "code": "EMAIL_ALREADY_EXISTS",
                "field": "Correo",
                "value": usuario.Correo
            }
        )
    
    # 2. Verificar tipo de usuario (forma asíncrona)
    result = await db.execute(
        select(TipoUsuario).where(TipoUsuario.IdTipoUsuario == usuario.IdTipoUsuario)
    )
    if not result.scalars().first():
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
        # 3. Crear el nuevo usuario
        nuevo_usuario = Usuario(
            IdTipoUsuario=usuario.IdTipoUsuario,
            NombreUsuario=usuario.NombreUsuario,
            Correo=usuario.Correo,
            Telefono=usuario.Telefono,
            Clave=hash_password(usuario.Clave),  # Hasheo seguro
            Nombres=usuario.Nombres,
            Apellidos=usuario.Apellidos,
            Estado=usuario.Estado,
            FechaNacimiento=usuario.FechaNacimiento,
            UrlPerfil=usuario.UrlPerfil,
            FechaCreacion=datetime.now().replace(tzinfo=None)  # <-- quita la zona horaria

        )
        
        db.add(nuevo_usuario)
        await db.commit()
        await db.refresh(nuevo_usuario)
        return nuevo_usuario
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al crear usuario",
                "code": "USER_CREATION_ERROR",
                "details": str(e)
            }
        )

@router.post("/login", response_model=LoginResponseModel)
async def login_user(
    login_data: UsuarioLoginModel, 
    session: AsyncSession = Depends(get_session)
):
    # Verificar usuario
    usuario = await UsuarioService.getUsuarioByEmail(login_data.Correo, session)
    
    if not usuario or not usuario.Clave:
        raise HTTPException(status_code=400, detail="Usuario sin contraseña registrada")

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    # Verificar contraseña
    if not verify_password(login_data.Clave, usuario.Clave):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    # Crear tokens
    access_token = createAccessToken(usuario=usuario)
    refresh_token = createAccessToken(
        usuario=usuario,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
        refresh=True
    )

    # Preparar respuesta de acuerdo con el nuevo modelo de respuesta
    return LoginResponseModel(
        status_code=status.HTTP_200_OK,
        message="Login exitoso",
        tokens=TokenModel(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        ),
        usuario=UsuarioResponseModel(
            id=usuario.IdUsuario,
            email=usuario.Correo,
            nombre=f"{usuario.Nombres} {usuario.Apellidos}"
        )
    )


@router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        # Crear instancia de Usuario con solo los campos necesarios
        usuario = Usuario(
            IdUsuario=token_details['IdUsuario'],
            Correo=token_details['Correo'],
            NombreUsuario=token_details['NombreUsuario']
        )

        new_access_token = createAccessToken(usuario=usuario)

        return JSONResponse(
            content={"access_token": new_access_token, "token_type": "bearer"},
            status_code=status.HTTP_200_OK
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El token de actualización ha expirado o no es válido"
    )

#Obtener todos los usuarios
@router.get("/usuario", response_model=List[UsuarioResponse])
async def obtener_usuario(db: AsyncSession = Depends(get_db), user_details=Depends(access_token_bearer)):
    async with db as session:
        result = await session.execute(select(Usuario))
        return result.scalars().all()
    
#Obtener un usuario por su id


@router.get("/usuario/{id}", response_model=UsuarioResponse)
async def obtener_usuario_por_id(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Usuario).where(Usuario.IdUsuario == id))
        usuario = result.scalars().first()
        if usuario is None:
            raise HTTPException(status_code=404, detail="No existe esa unidad de medida")
        return usuario



#Actualizar un usuario
@router.put("/usuario/{id}", response_model=UsuarioResponse)
async def actualizar_usuario(id: int, usuarioParam: UsuarioUpdate, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Buscar usuario existente
        result = await db.execute(select(Usuario).where(Usuario.IdUsuario == id))
        usuario = result.scalars().first()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Usuario no encontrado", "id": id}
            )

        # 2. Obtener solo campos modificados (excluyendo los que no se enviaron)
        update_data = usuarioParam.model_dump(exclude_unset=True)

        # 3. Validaciones
        if "Correo" in update_data:
            # Verificar formato de correo
            if not re.match(r"[^@]+@[^@]+\.[^@]+", update_data["Correo"]):
                raise ValueError("El correo electrónico no tiene un formato válido")

            # Verificar duplicado
            result = await db.execute(
                select(Usuario).where(
                    Usuario.Correo == update_data["Correo"],
                    Usuario.IdUsuario != id
                )
            )
            if result.scalars().first():
                raise ValueError("El correo ya está registrado por otro usuario")

        if "Telefono" in update_data:
            if not update_data["Telefono"].isdigit():
                raise ValueError("El teléfono debe contener solo números")

        if "NombreUsuario" in update_data:
            result = await db.execute(
                select(Usuario).where(
                    Usuario.NombreUsuario == update_data["NombreUsuario"],
                    Usuario.IdUsuario != id
                )
            )
            if result.scalars().first():
                raise ValueError("El nombre de usuario ya está en uso")

        # 4. Aplicar actualizaciones
        for field, value in update_data.items():
            setattr(usuario, field, value)

        await db.commit()
        await db.refresh(usuario)
        return usuario

    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error de validación", "message": str(ve)}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar usuario", "details": str(e)}
        )

#Eliminar un usuario
@router.delete("/usuario/{id}", response_model=UsuarioResponse)
async def eliminar_usuario(id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Usuario).where(Usuario.IdUsuario == id))
        usuario = result.scalars().first()

        if usuario is None:
            raise HTTPException(status_code=404, detail="No existe ese usuario")

        await session.delete(usuario)
        await session.commit()
#
        return usuario  # ← Devuelve el objeto antes de eliminarlo en la sesión

@router.put("/change-password", response_model=UsuarioResponse)
async def cambiar_contraseña(datos: UsuarioUpdatePassword, db: AsyncSession = Depends(get_db)):
    try:
        # Buscar al usuario por ID
        result = await db.execute(select(Usuario).where(Usuario.IdUsuario == datos.IdUsuario))
        usuario_db = result.scalars().first()

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

        # Actualizar la clave nueva
        usuario_db.Clave = hash_password(datos.ClaveNueva)
        await db.commit()
        await db.refresh(usuario_db)

        return usuario_db

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar contraseña", "details": str(e)}
        )
       

#Hashar la contraseña
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Lo guardas como string en la DB


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

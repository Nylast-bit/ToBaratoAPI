from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Usuario, TipoUsuario, OTP, Producto, UsuarioProveedor, ListaProducto, Lista, ProductoProveedor
from app.schemas.producto import ProductoResponse, ProductoSugeridoResponse
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate, UsuarioUpdatePassword, UsuarioLoginModel, LoginResponseModel, TokenModel, UsuarioResponseModel
import bcrypt
from sqlalchemy import func

from app.auth.utils import createAccessToken, decodeAccessToken
from app.auth.service import UsuarioService
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime
from app.dependencies import get_session
from app.database import AsyncSessionLocal
from app.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from app.utils import (
    generar_codigo_otp,
    obtener_expiracion_otp,
    validar_correo,
    enviar_correo_otp
)

import re
from sqlalchemy.future import select


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




@router.post("/signup", response_model=UsuarioResponse)
async def crear_usuario(usuario: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    # 1. Verificar si el correo ya está registrado
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

    # 2. Verificar tipo de usuario
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

    # 3. Verificar OTP
    otp_result = await db.execute(
        select(OTP)
        .where(OTP.Email == usuario.Correo)
        .order_by(OTP.ExpiresAt.desc())
    )
    otp = otp_result.scalars().first()

    if not otp :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                "error": "OTP inválido o expirado",
                "code": "OTP_INVALID_OR_EXPIRED"
            }
        )

    try:
        # 4. Crear el nuevo usuario
        nuevo_usuario = Usuario(
            IdTipoUsuario=usuario.IdTipoUsuario,
            NombreUsuario=usuario.NombreUsuario,
            Correo=usuario.Correo,
            Telefono=usuario.Telefono,
            Clave=hash_password(usuario.Clave),
            Nombres=usuario.Nombres,
            Apellidos=usuario.Apellidos,
            Estado=usuario.Estado,
            FechaNacimiento=usuario.FechaNacimiento,
            UrlPerfil=usuario.UrlPerfil,
            FechaCreacion=datetime.now().replace(tzinfo=None)
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
    
#Obtener todos los usuarios
@router.get("/otp", response_model=List[UsuarioResponse])
async def obtener_usuario(db: AsyncSession = Depends(get_db), user_details=Depends(access_token_bearer)):
    async with db as session:
        result = await session.execute(select(OTP))
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


#Sugerencias para productos de una lista de un usuario 
@router.get("/sugerencias/{id_usuario}", response_model=list[ProductoSugeridoResponse])
async def sugerir_productos(id_usuario: int, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Buscar proveedores más frecuentes del usuario
        result = await db.execute(
            select(
                UsuarioProveedor.IdProveedor,
                func.count(UsuarioProveedor.IdProveedor).label("total")
            )
            .where(UsuarioProveedor.IdUsuario == id_usuario)
            .group_by(UsuarioProveedor.IdProveedor)
            .order_by(func.count(UsuarioProveedor.IdProveedor).desc())
        )
        proveedores_mas_frecuentes = result.all()

        if not proveedores_mas_frecuentes:
            raise HTTPException(status_code=404, detail="El usuario no tiene proveedores registrados")

        ids_proveedores_top = [p[0] for p in proveedores_mas_frecuentes]

        # 2. Buscar productos de esos proveedores (con precio)
        result_productos = await db.execute(
            select(
                ProductoProveedor.IdProducto,
                ProductoProveedor.IdProveedor,
                ProductoProveedor.Precio
            ).where(ProductoProveedor.IdProveedor.in_(ids_proveedores_top))
        )
        productos_por_proveedor = result_productos.all()

        if not productos_por_proveedor:
            raise HTTPException(status_code=404, detail="No hay productos registrados para esos proveedores")

        # Mapear producto_id -> (proveedor_id, precio)
        producto_proveedor_map = {
            producto_id: (proveedor_id, precio)
            for producto_id, proveedor_id, precio in productos_por_proveedor
        }

        ids_productos = list(producto_proveedor_map.keys())

        # 3. Buscar productos más frecuentes en listas del usuario
        result_frecuencia = await db.execute(
            select(
                ListaProducto.IdProducto,
                func.count(ListaProducto.IdProducto).label("cantidad")
            )
            .join(Lista, ListaProducto.IdLista == Lista.IdLista)
            .where(
                Lista.IdUsuario == id_usuario,
                ListaProducto.IdProducto.in_(ids_productos)
            )
            .group_by(ListaProducto.IdProducto)
            .order_by(func.count(ListaProducto.IdProducto).desc())
            .limit(10)
        )
        productos_frecuentes = result_frecuencia.all()

        if not productos_frecuentes:
            raise HTTPException(status_code=404, detail="No se encontraron productos en listas del usuario")

        productos_ids_frecuentes = [p[0] for p in productos_frecuentes]

        # 4. Obtener información completa de esos productos
        result_final = await db.execute(
            select(Producto).where(Producto.IdProducto.in_(productos_ids_frecuentes))
        )
        productos = result_final.scalars().all()

        # 5. Armar respuesta final
        sugerencias = []
        for producto in productos:
            proveedor_info = producto_proveedor_map.get(producto.IdProducto)
            if proveedor_info:
                proveedor_id, precio = proveedor_info
                sugerencias.append(ProductoSugeridoResponse(
                    IdProducto=producto.IdProducto,
                    NombreProducto=producto.Nombre,
                    IdProveedor=proveedor_id,
                    Precio=precio
                ))

        return sugerencias

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al sugerir productos: {str(e)}")

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
       



@router.post("/solicitar-otp")
async def solicitar_otp(email: EmailStr, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).where(Usuario.Correo == email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    code = generar_codigo_otp()
    expires_at = datetime.now() + timedelta(minutes=10)

    nuevo_otp = OTP(Email=email, Code=code, ExpiresAt=expires_at)
    db.add(nuevo_otp)
    await db.commit()

    await enviar_correo_otp(email, code)  # Tu función de envío

    return {"message": "OTP enviado exitosamente"}

@router.post("/verificar-otp")
async def verificar_otp(email: EmailStr, codigo: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OTP).where(OTP.Email == email).order_by(OTP.ExpiresAt.desc())
    )
    otp = result.scalars().first()

    if not otp or otp.Code != codigo:
        raise HTTPException(status_code=400, detail="Código inválido")

    if otp.ExpiresAt < datetime.now():
        raise HTTPException(status_code=400, detail="Código expirado")

    return {"message": "OTP verificado exitosamente"}


#Hashar la contraseña
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Lo guardas como string en la DB


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

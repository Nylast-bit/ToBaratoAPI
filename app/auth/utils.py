from app.models.models import Usuario
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt 
import uuid
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import ExpiredSignatureError, PyJWTError

load_dotenv()

jwt_secret = os.getenv("JWT_SECRET")
jwt_algorithm = os.getenv("JWT_ALGORITHM")

ACCESS_TOKEN_EXPIRY = 3600


def createAccessToken(usuario: Usuario, expiry: timedelta = None, refresh: bool = False):
    # Aquí aseguramos que estamos accediendo a los atributos de la clase correctamente

    payload = {
        "IdUsuario": usuario.IdUsuario,
        "Correo": usuario.Correo,
        "NombreUsuario": usuario.NombreUsuario,
        "exp": datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(
        payload=payload,
        key=jwt_secret,
        algorithm=jwt_algorithm,
    )

    return token

def decodeAccessToken(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=jwt_secret,
            algorithms=[jwt_algorithm],
        )
        return token_data
    except ExpiredSignatureError:
        logging.error("Token expirado")
        return None
    except PyJWTError as e:
        logging.exception("Error decoding JWT token: %s", e)
        return None
    
    

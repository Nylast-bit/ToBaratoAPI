from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional


class UsuarioBase(BaseModel):
    IdTipoUsuario: int = Field(..., alias="IdTipoUsuario") # ← Debe coincidir con el modelo SQLAlchemy
    NombreUsuario: str = Field(..., alias="NombreUsuario")  # ← Debe coincidir con el modelo SQLAlchemy
    Correo: EmailStr = Field(..., alias="Correo")   # ← Debe coincidir con el modelo SQLAlchemy
    Telefono: str = Field(..., alias="Telefono") # ← Debe coincidir con el modelo SQLAlchemy
    Clave: str = Field(...,exclude=True, alias="Clave") # ← Debe coincidir con el modelo SQLAlchemy
    Nombres: str = Field(..., alias="Nombres")
    Apellidos: str = Field(..., alias="Apellidos")
    Estado: bool = Field(..., alias="Estado")
    UrlPerfil: Optional[str] = Field(None, alias="UrlPerfil")
    FechaNacimiento: datetime = Field(..., alias="FechaNacimiento")

    

class UsuarioCreate(UsuarioBase):
    Estado: bool = True
    pass


class UsuarioUpdate(BaseModel):
    IdTipoUsuario: Optional[int] = Field(None, alias="IdTipoUsuario")
    NombreUsuario: Optional[str] = Field(None, alias="NombreUsuario")
    Correo: Optional[EmailStr] = Field(None, alias="Correo")
    Telefono: Optional[str] = Field(None, alias="Telefono")
    Nombres: Optional[str] = Field(None, alias="Nombres")
    Apellidos: Optional[str] = Field(None, alias="Apellidos")
    Estado: Optional[bool] = Field(None, alias="Estado")
    UrlPerfil: Optional[str] = Field(None, alias="UrlPerfil")
    FechaNacimiento: Optional[datetime] = Field(None, alias="FechaNacimiento")

class UsuarioUpdatePassword(BaseModel):
    IdUsuario: int
    Clave: str
    ClaveNueva: str
class UsuarioResponse(UsuarioBase):
    IdUsuario: int  # ← Nombre exacto como en el modelo
    FechaCreacion: datetime

    class Config:
        from_attributes = True



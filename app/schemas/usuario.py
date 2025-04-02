from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, Field

class UsuarioBase(BaseModel):
    IdTipoUsuario: int = Field(..., alias="IdTipoUsuario") # ← Debe coincidir con el modelo SQLAlchemy
    NombreUsuario: str = Field(..., alias="NombreUsuario")  # ← Debe coincidir con el modelo SQLAlchemy
    Correo: EmailStr = Field(..., alias="Correo")   # ← Debe coincidir con el modelo SQLAlchemy
    Telefono: str = Field(..., alias="Telefono") # ← Debe coincidir con el modelo SQLAlchemy
    Clave: str = Field(..., alias="Clave")
    Nombres: str = Field(..., alias="Nombres")
    Apellidos: str = Field(..., alias="Apellidos")
    Estado: bool = Field(..., alias="Estado")
    UrlPerfil: str = Field(..., alias="UrlPerfil")
    FechaNacimiento: datetime = Field(..., alias="FechaNacimiento")

    

class UsuarioCreate(UsuarioBase):
    Estado: bool = True
    pass

class UsuarioResponse(UsuarioBase):
    IdUsuario: int  # ← Nombre exacto como en el modelo
    FechaCreacion: datetime

    class Config:
        from_attributes = True
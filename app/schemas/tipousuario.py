from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field

class TipoUsuarioBase(BaseModel):
    NombreTipoUsuario: str = Field(..., alias="nombre") # ← Debe coincidir con el modelo SQLAlchemy

class TipoUsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)  # Coincide con el JSON que envías

class TipoUsuarioResponse(BaseModel):
    id: int = Field(..., alias="IdTipoUsuario")  # Mapea IdTipoUsuario de SQLAlchemy a id
    NombreTipoUsuario: str = Field(..., alias="nombre_tipo_usuario")
    fecha_creacion: datetime = Field(..., alias="FechaCreacion")

    class Config:
        from_attributes = True
        populate_by_name = True  # Permite trabajar con alias
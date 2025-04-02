from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field

class TipoUsuarioBase(BaseModel):
    NombreTipoUsuario: str = Field(..., alias="NombreTipoUsuario") # ← Debe coincidir con el modelo SQLAlchemy

class TipoUsuarioCreate(TipoUsuarioBase):
    pass

class TipoUsuarioResponse(TipoUsuarioBase):
    IdTipoUsuario: int  # ← Nombre exacto como en el modelo
    FechaCreacion: datetime

    class Config:
        from_attributes = True
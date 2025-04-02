from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field

class UnidadMedidaBase(BaseModel):
    NombreUnidadMedida: str  = Field(..., alias="NombreUnidadMedida")# ← Debe coincidir con el modelo SQLAlchemy

class UnidadMedidaCreate(UnidadMedidaBase):
    pass

class UnidadMedidaResponse(UnidadMedidaBase):
    IdUnidadMedida: int  # ← Nombre exacto como en el modelo
    FechaCreacion: datetime

    class Config:
        from_attributes = True
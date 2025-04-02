from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field

class TipoProveedorBase(BaseModel):
    NombreTipoProveedor: str = Field(..., alias="NombreTipoProveedor") # ← Debe coincidir con el modelo SQLAlchemy

class TipoProveedorCreate(TipoProveedorBase):
    pass

class TipoProveedorResponse(TipoProveedorBase):
    IdTipoProveedor: int  # ← Nombre exacto como en el modelo
    FechaCreacion: datetime

    class Config:
        from_attributes = True
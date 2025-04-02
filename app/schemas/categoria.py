from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field

class CategoriaBase(BaseModel):
    NombreCategoria: str = Field(..., alias="NombreCategoria") # ← Debe coincidir con el modelo SQLAlchemy

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    IdCategoria: int  # ← Nombre exacto como en el modelo
    FechaCreacion: datetime

    class Config:
        from_attributes = True
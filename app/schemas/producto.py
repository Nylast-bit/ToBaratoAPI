from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional

class ProductoBase(BaseModel):
    IdCategoria: int = Field(..., alias="IdCategoria")
    IdUnidadMedida: int = Field(..., alias="IdUnidadMedida")
    Nombre: str = Field(..., max_length=100, alias="Nombre")
    UrlImagen: str = Field(..., alias="UrlImagen")
    Descripcion: Optional[str] = Field(None, max_length=300, alias="Descripcion")


class ProductoCreate(ProductoBase):
    
    pass

class ProductoUpdate(BaseModel):
    IdCategoria: Optional[int] = Field(None, alias="IdCategoria")
    IdUnidadMedida: Optional[int] = Field(None, alias="IdUnidadMedida")
    Nombre: Optional[str] = Field(None, max_length=100, alias="Nombre")
    UrlImagen: Optional[str] = Field(None, alias="UrlImagen")
    Descripcion: Optional[str] = Field(None, max_length=300, alias="Descripcion")

class ProductoResponse(ProductoBase):
    IdProducto: int 
    FechaCreacion: datetime 
    
    class Config:
        from_attributes = True
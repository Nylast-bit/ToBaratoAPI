from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import Optional

class ListaProductoBase(BaseModel):
    IdLista: int = Field(..., alias="IdLista")
    IdProducto: int = Field(..., alias="IdProducto")
    PrecioActual: Decimal = Field(..., alias="PrecioActual")
    Cantidad: int = Field(..., alias="Cantidad")

class ListaProductoCreate(ListaProductoBase):
    @field_validator('PrecioActual')
    def precio_positivo(cls, v):
        if v <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        return v

    @field_validator('Cantidad')
    def cantidad_positiva(cls, v):
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        return v

class ListaProductoUpdate(BaseModel):
    PrecioActual: Optional[Decimal] = Field(None, alias="PrecioActual")
    Cantidad: Optional[int] = Field(None, alias="Cantidad")

    @field_validator('PrecioActual')
    def precio_positivo(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        return v

    @field_validator('Cantidad')
    def cantidad_positiva(cls, v):
        if v is not None and v <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        return v
    
    
class ListaProductoResponse(ListaProductoBase):
    # En este caso no agregamos campos adicionales ya que es una tabla de relación
    class Config:
        from_attributes = True
        orm_mode = True
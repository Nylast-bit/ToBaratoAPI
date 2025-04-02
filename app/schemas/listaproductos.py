from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class ListaProductoBase(BaseModel):
    IdLista: int = Field(..., alias="IdLista")
    IdProducto: int = Field(..., alias="IdProducto")
    PrecioActual: Decimal = Field(..., alias="PrecioActual")
    Cantidad: int = Field(..., alias="Cantidad")

class ListaProductoCreate(ListaProductoBase):
    pass

class ListaProductoResponse(ListaProductoBase):
    # En este caso no agregamos campos adicionales ya que es una tabla de relación
    class Config:
        from_attributes = True
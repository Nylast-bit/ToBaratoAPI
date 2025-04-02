from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class ListaBase(BaseModel):
    IdUsuario: int = Field(..., alias="IdUsuario")
    IdProveedor: int = Field(..., alias="IdProveedor")
    Nombre: str = Field(..., max_length=100, alias="Nombre")
    PrecioTotal: Decimal = Field(..., alias="PrecioTotal")


class ListaCreate(ListaBase):
    pass

class ListaResponse(ListaBase):
    IdLista: int = Field(..., alias="IdLista")
    FechaCreacion: datetime


    class Config:
        from_attributes = True
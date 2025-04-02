from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UsuarioProveedorBase(BaseModel):
    IdProveedor: int = Field(..., alias="IdProveedor")
    IdUsuario: int = Field(..., alias="IdUsuario")
    ProductosComprados: int = Field(..., alias="ProductosComprados")
    FechaUltimaCompra: datetime = Field(..., alias="FechaUltimaCompra")
    Preferencia: bool = Field(..., alias="Preferencia")

class UsuarioProveedorCreate(UsuarioProveedorBase):
    pass

class UsuarioProveedorResponse(UsuarioProveedorBase):
    # En este caso no agregamos campos adicionales ya que es una tabla de relación
    class Config:
        from_attributes = True
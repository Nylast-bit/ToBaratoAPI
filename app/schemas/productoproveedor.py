from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional

class ProductoProveedorBase(BaseModel):
    IdProducto: int = Field(..., alias="IdProducto")
    IdProveedor: int = Field(..., alias="IdProveedor")
    Precio: Decimal = Field(..., alias="Precio")
    PrecioOferta: Optional[Decimal] = Field(None, alias="PrecioOferta")
    DescripcionOferta: Optional[str] = Field("No habia oferta", alias="DescripcionOferta")
    FechaOferta: datetime = Field(..., alias="FechaOferta")
    FechaPrecio: datetime = Field(..., alias="FechaPrecio")

class ProductoProveedorCreate(ProductoProveedorBase):
    pass

class ProductoProveedorResponse(ProductoProveedorBase):
    # En este caso no agregamos campos adicionales ya que es una tabla de relación

    class Config:
        from_attributes = True
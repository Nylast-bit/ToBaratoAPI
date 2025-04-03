from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional

class ProductoProveedorBase(BaseModel):
    IdProducto: int = Field(..., alias="IdProducto")
    IdProveedor: int = Field(..., alias="IdProveedor")
    Precio: Decimal = Field(..., alias="Precio")
    PrecioOferta: Optional[Decimal] = Field(None, alias="PrecioOferta")
    DescripcionOferta: Optional[str] = Field("No habia oferta", alias="DescripcionOferta")
    FechaOferta: Optional[datetime] = Field(None, alias="FechaOferta")
    FechaPrecio: datetime = Field(..., alias="FechaPrecio")

class ProductoProveedorCreate(ProductoProveedorBase):
    pass

class ProductoProveedorUpdate(BaseModel):
    Precio: Optional[Decimal] = Field(alias="Precio")
    PrecioOferta: Optional[Decimal] = Field(alias="PrecioOferta")
    DescripcionOferta: Optional[str] = Field(alias="DescripcionOferta")
    FechaOferta: Optional[datetime] = Field(alias="FechaOferta")
    FechaPrecio: Optional[datetime] = Field(alias="FechaPrecio")

    @field_validator('Precio', 'PrecioOferta')
    def validar_precios(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        return v

    @field_validator('FechaOferta', 'FechaPrecio')
    def validar_fechas_futuras(cls, v):
        if v is not None and v > datetime.now():
            raise ValueError("Las fechas no pueden ser futuras")
        return v

class ProductoProveedorResponse(ProductoProveedorBase):
    # En este caso no agregamos campos adicionales ya que es una tabla de relación

    class Config:
        from_attributes = True
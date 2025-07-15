from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Float
from decimal import Decimal


class ProductoBase(BaseModel):
    IdCategoria: int = Field(..., alias="IdCategoria")
    IdUnidadMedida: int = Field(..., alias="IdUnidadMedida")
    Nombre: str = Field(..., max_length=100)
    UrlImagen: Optional[str] = Field(None, alias="UrlImagen")
    Descripcion: Optional[str] = Field(None, max_length=300, alias="Descripcion")


class ProductoCreate(ProductoBase):
    
    pass

class ProductoUpdate(BaseModel):
    IdCategoria: Optional[int] = Field(None, alias="IdCategoria")
    IdUnidadMedida: Optional[int] = Field(None, alias="IdUnidadMedida")
    NombreProducto: Optional[str] = Field(None, max_length=100, alias="Nombre")
    UrlImagen: Optional[str] = Field(None, alias="UrlImagen")
    Descripcion: Optional[str] = Field(None, max_length=300, alias="Descripcion")


class ProductoSugeridoResponse(BaseModel):
    IdProducto: int
    NombreProducto: str
    IdProveedor: int
    Precio: float

class ProductoConPrecioPromedioResponse(BaseModel):
    IdProducto: int
    IdCategoria: int
    IdUnidadMedida: int
    Nombre: str
    UrlImagen: Optional[str]
    Descripcion: Optional[str]
    FechaCreacion: datetime
    PrecioPromedio: Optional[float]

class BigProductoProveedorResponse(BaseModel):
    IdProducto: int
    IdProveedor: int
    Precio: Decimal
    PrecioOferta: Optional[Decimal]
    DescripcionOferta: Optional[str]
    FechaOferta: Optional[datetime]
    FechaPrecio: Optional[datetime]
    Producto: ProductoBase

class ProductoPrecioProveedorResponse(BaseModel):
    IdProveedor: int
    NombreProveedor: str
    UrlImagenProveedor: Optional[str]
    Precio: Decimal
    PrecioOferta: Optional[Decimal]
    DescripcionOferta: Optional[str]
    FechaOferta: Optional[datetime]
    FechaPrecio: Optional[datetime]


class ProductoResponse(ProductoBase):
    IdProducto: int 
    FechaCreacion: datetime 
    
    class Config:
        from_attributes = True

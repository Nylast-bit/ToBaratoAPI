from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import pytz

class SucursalBase(BaseModel):
    IdProveedor: int = Field(..., alias="IdProveedor")
    NombreSucursal: str = Field(..., alias="NombreSucursal", max_length=100)
    latitud: str = Field(..., alias="Latitud")
    longitud: str = Field(..., alias="Longitud")

class SucursalCreate(SucursalBase):
    @field_validator('NombreSucursal')
    def validar_nombre(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        return v


class SucursalUpdate(BaseModel):
    IdProveedor: Optional[int] = Field(None, alias="IdProveedor")
    NombreSucursal: Optional[str] = Field(None, alias="NombreSucursal", max_length=100)
    latitud: Optional[str] = Field(None, alias="latitud", max_length=300)
    longitud: Optional[str] = Field(None, alias="longitud", max_length=300)

    @field_validator('NombreSucursal')
    def validar_nombre(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) < 3:
                raise ValueError("El nombre debe tener al menos 3 caracteres")
        return v

    @field_validator('latitud', 'longitud')
    def validar_coordenadas(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Las coordenadas no pueden estar vacías")
            try:
                float(v)
            except ValueError:
                raise ValueError("Las coordenadas deben ser valores numéricos")
        return v

class ProductoSucursalResponse(BaseModel):
    NombreSucursal: str
    Latitud: float
    Longitud: float
    IdProveedor: int
    Precio: float
    Distancia: float
    
class UbicacionProductoRequest(BaseModel):
    lat: float
    lng: float
    id_producto: int

class SucursalResponse(SucursalBase):
    IdSucursal: int = Field(..., alias="IdSucursal")
    FechaCreacion: datetime = Field(..., alias="FechaCreacion")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.astimezone(pytz.timezone('America/La_Paz')).isoformat()
        }
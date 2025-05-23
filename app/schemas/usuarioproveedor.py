from pydantic import BaseModel, Field, field_validator
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




class UsuarioProveedorUpdate(BaseModel):
    ProductosComprados: Optional[int] = Field(
        None,
        alias="ProductosComprados",
        description="Cantidad de productos comprados (opcional)",
        example=15
    )
    FechaUltimaCompra: Optional[datetime] = Field(
        None,
        alias="FechaUltimaCompra",
        description="Fecha de última compra (opcional)",
        example="2023-11-20T14:30:00"
    )
    Preferencia: Optional[bool] = Field(
        None,
        alias="Preferencia",
        description="Si es proveedor preferente (opcional)",
        example=True
    )

    @field_validator('ProductosComprados')
    def validar_productos_comprados(cls, v):
        if v is not None and v < 0:
            raise ValueError("Los productos comprados no pueden ser negativos")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "Preferencia": False,
                "ProductosComprados": 20
            }
        }

class UsuarioProveedorResponse(UsuarioProveedorBase):
    IdUsuarioProveedor: int
    # En este caso no agregamos campos adicionales ya que es una tabla de relación
    class Config:
        from_attributes = True
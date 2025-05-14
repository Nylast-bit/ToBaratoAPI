from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProveedorBase(BaseModel):
    IdTipoProveedor: int = Field(..., alias = "IdTipoProveedor")
    Nombre: str = Field(..., max_length=100, description="Nombre del proveedor")
    UrlLogo: Optional[str] = Field(..., max_length=300, description="URL del logo del proveedor")
    UrlPaginaWeb: Optional[str] = Field(None, max_length=300, description="URL de la página web del proveedor")
    EnvioDomicilio: Optional[bool] = Field(None, description="¿Realiza envíos a domicilio?")

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    IdTipoProveedor: Optional[int] = Field(None, alias="IdTipoProveedor")
    Nombre: Optional[str] = Field(None, max_length=100,alias="Nombre")
    UrlLogo: Optional[str] = Field(max_length=300, alias="UrlLogo")
    UrlPaginaWeb: Optional[str] = Field(max_length=300,alias="UrlPaginaWeb")
    EnvioDomicilio: Optional[bool] = Field(alias="EnvioDomicilio" )

class ProveedorResponse(ProveedorBase):
    IdProveedor: int 
    FechaCreacion: datetime 
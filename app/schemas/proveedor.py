from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProveedorBase(BaseModel):
    IdTipoProveedor: int = Field(..., alias = "IdTipoProveedor")
    Nombre: str = Field(..., max_length=100, description="Nombre del proveedor")
    UrlLogo: str = Field(..., max_length=300, description="URL del logo del proveedor")
    UrlPaginaWeb: Optional[str] = Field(None, max_length=300, description="URL de la página web del proveedor")
    EnvioDomicilio: Optional[bool] = Field(None, description="¿Realiza envíos a domicilio?")

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorResponse(ProveedorBase):
    IdProveedor: int 
    FechaCreacion: datetime 
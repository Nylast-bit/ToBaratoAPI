from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship, declarative_base
from app.database import Base
from datetime import datetime
import pytz


def now_bolivia():
    return datetime.now(pytz.timezone('America/La_Paz'))

class TipoUsuario(Base):
    __tablename__ = 'TipoUsuario'
    
    IdTipoUsuario = Column(Integer, primary_key=True, autoincrement=True)
    NombreTipoUsuario = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime(timezone=True), default=now_bolivia)
    
    Usuarios = relationship("Usuario", back_populates="TipoUsuario")

class TipoProveedor(Base):
    __tablename__ = 'TipoProveedor'
    
    IdTipoProveedor = Column(Integer, primary_key=True, autoincrement=True)
    NombreTipoProveedor = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Proveedores = relationship("Proveedor", back_populates="TipoProveedor")

class Categoria(Base):
    __tablename__ = 'Categoria'
    
    IdCategoria = Column(Integer, primary_key=True, autoincrement=True)
    NombreCategoria = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Productos = relationship("Producto", back_populates="Categoria")

class UnidadMedida(Base):
    __tablename__ = 'UnidadMedida'
    
    IdUnidadMedida = Column(Integer, primary_key=True, autoincrement=True)
    NombreUnidadMedida = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Productos = relationship("Producto", back_populates="UnidadMedida")

class Usuario(Base):
    __tablename__ = 'Usuario'
    
    IdUsuario = Column(Integer, primary_key=True, autoincrement=True)
    IdTipoUsuario = Column(Integer, ForeignKey('TipoUsuario.IdTipoUsuario'), nullable=False)
    NombreUsuario = Column(String(100), unique=True)
    Correo = Column(String(255), unique=True, nullable=False)
    Telefono = Column(String(15), nullable=False)
    Clave = Column(String(255), nullable=False)
    Nombres = Column(String(100), nullable=False)
    Apellidos = Column(String(100), nullable=False)
    Estado = Column(Boolean, nullable=False, default=True)
    UrlPerfil = Column(Text)
    FechaNacimiento = Column(DateTime, nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    TipoUsuario = relationship("TipoUsuario", back_populates="Usuarios")
    Listas = relationship("Lista", back_populates="Usuario")
    Proveedores = relationship("UsuarioProveedor", back_populates="Usuario")

class Proveedor(Base):
    __tablename__ = 'Proveedor'
    
    IdProveedor = Column(Integer, primary_key=True, autoincrement=True)
    IdTipoProveedor = Column(Integer, ForeignKey('TipoProveedor.IdTipoProveedor'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    UrlLogo = Column(Text, nullable=True)
    UrlPaginaWeb = Column(Text)
    EnvioDomicilio = Column(Boolean)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    TipoProveedor = relationship("TipoProveedor", back_populates="Proveedores")
    Listas = relationship("Lista", back_populates="Proveedor")
    Productos = relationship("ProductoProveedor", back_populates="Proveedor")
    Usuarios = relationship("UsuarioProveedor", back_populates="Proveedor")
    Sucursales = relationship("Sucursal", back_populates="Proveedor")

class Sucursal(Base):
    __tablename__ = 'Sucursal'
    
    IdSucursal = Column(Integer, primary_key=True, autoincrement=True)
    IdProveedor = Column(Integer, ForeignKey('Proveedor.IdProveedor'), nullable=False)
    NombreSucursal = Column(String(100), nullable=False)
    Latitud = Column("latitud", String(100), nullable=False)
    Longitud = Column("longitud", String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Proveedor = relationship("Proveedor", back_populates="Sucursales")

class Producto(Base):
    __tablename__ = 'Producto'
    
    IdProducto = Column(Integer, primary_key=True, autoincrement=True)
    IdCategoria = Column(Integer, ForeignKey('Categoria.IdCategoria'), nullable=False)
    IdUnidadMedida = Column(Integer, ForeignKey('UnidadMedida.IdUnidadMedida'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    UrlImagen = Column(Text, nullable=False)
    Descripcion = Column(Text)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Categoria = relationship("Categoria", back_populates="Productos")
    UnidadMedida = relationship("UnidadMedida", back_populates="Productos")
    Listas = relationship("ListaProducto", back_populates="Producto")
    Proveedores = relationship("ProductoProveedor", back_populates="Producto")

class Lista(Base):
    __tablename__ = 'Lista'
    
    IdLista = Column(Integer, primary_key=True, autoincrement=True)
    IdUsuario = Column(Integer, ForeignKey('Usuario.IdUsuario'), nullable=False)
    IdProveedor = Column(Integer, ForeignKey('Proveedor.IdProveedor'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    PrecioTotal = Column(Numeric(10, 2), nullable=False, default=0.00)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Usuario = relationship("Usuario", back_populates="Listas")
    Proveedor = relationship("Proveedor", back_populates="Listas")
    
    Productos = relationship(
        "ListaProducto",
        back_populates="Lista",
        cascade="all, delete-orphan"
    )


class ListaProducto(Base):
    __tablename__ = 'ListaProducto'
    __table_args__ = (
        PrimaryKeyConstraint('IdLista', 'IdProducto'),
        ForeignKeyConstraint(['IdLista'], ['Lista.IdLista']),
        ForeignKeyConstraint(['IdProducto'], ['Producto.IdProducto']),
    )
    
    IdLista = Column(Integer)
    IdProducto = Column(Integer)
    PrecioActual = Column(Numeric(10, 2), nullable=False)
    Cantidad = Column(Integer, nullable=False, default=1)
    
    Lista = relationship("Lista", back_populates="Productos")
    Producto = relationship("Producto", back_populates="Listas")


class UsuarioProveedor(Base):
    __tablename__ = 'UsuarioProveedor'
    
    # Nueva clave primaria única
    IdUsuarioProveedor = Column(Integer, primary_key=True, autoincrement=True)
    IdProveedor = Column(Integer, ForeignKey('Proveedor.IdProveedor'))
    IdUsuario = Column(Integer, ForeignKey('Usuario.IdUsuario'))
    ProductosComprados = Column(Integer, nullable=False, default=0)
    FechaUltimaCompra = Column(DateTime)
    Preferencia = Column(Boolean, nullable=False, default=False)
    
    # Relación con otras tablas
    Proveedor = relationship("Proveedor", back_populates="Usuarios")
    Usuario = relationship("Usuario", back_populates="Proveedores")




class ProductoProveedor(Base):
    __tablename__ = 'ProductoProveedor'
    __table_args__ = (
        PrimaryKeyConstraint('IdProducto', 'IdProveedor'),
    )
    
    IdProducto = Column(Integer, ForeignKey('Producto.IdProducto'))
    IdProveedor = Column(Integer, ForeignKey('Proveedor.IdProveedor'))
    Precio = Column(Numeric(10, 2), nullable=False)
    PrecioOferta = Column(Numeric(10, 2))
    DescripcionOferta = Column(Text)
    FechaOferta = Column(DateTime)
    FechaPrecio = Column(DateTime, nullable=False, default=now_bolivia)
    
    Producto = relationship("Producto", back_populates="Proveedores")
    Proveedor = relationship("Proveedor", back_populates="Productos")

class OTP(Base):
    __tablename__ = "OTP"
    
    Id = Column(Integer, primary_key=True)
    Email = Column(String(255), nullable=False)
    Code = Column(String(10), nullable=False)
    ExpiresAt = Column(DateTime, nullable=False)
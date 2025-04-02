from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import pytz

Base = declarative_base()

class TipoUsuario(Base):
    __tablename__ = 'TipoUsuario'
    
    IdTipoUsuario = Column(Integer, primary_key=True, autoincrement=True)
    NombreTipoUsuario = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
    Usuarios = relationship("Usuario", back_populates="TipoUsuario")

class TipoProveedor(Base):
    __tablename__ = 'TipoProveedor'
    
    IdTipoProveedor = Column(Integer, primary_key=True, autoincrement=True)
    NombreTipoProveedor = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
    Proveedores = relationship("Proveedor", back_populates="TipoProveedor")

class Categoria(Base):
    __tablename__ = 'Categoria'
    
    IdCategoria = Column(Integer, primary_key=True, autoincrement=True)
    NombreCategoria = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
    Productos = relationship("Producto", back_populates="Categoria")

class UnidadMedida(Base):
    __tablename__ = 'UnidadMedida'
    
    IdUnidadMedida = Column(Integer, primary_key=True, autoincrement=True)
    NombreUnidadMedida = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
    Productos = relationship("Producto", back_populates="UnidadMedida")

class Usuario(Base):
    __tablename__ = 'Usuario'
    
    IdUsuario = Column(Integer, primary_key=True, autoincrement=True)
    IdTipoUsuario = Column(Integer, ForeignKey('TipoUsuario.IdTipoUsuario'), nullable=False)
    NombreUsuario = Column(String(100))
    Correo = Column(String(100), unique=True, nullable=False)  # ← Debe ser único
    Telefono = Column(String(10), nullable=False)
    Clave = Column(String(100), nullable=False)
    Nombres = Column(String(100), nullable=False)
    Apellidos = Column(String(100), nullable=False)
    Estado = Column(Boolean, nullable=False)
    UrlPerfil = Column(String(300), nullable=True)
    FechaNacimiento = Column(DateTime, nullable=False)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
    TipoUsuario = relationship("TipoUsuario", back_populates="Usuarios")
    Listas = relationship("Lista", back_populates="Usuario")
    Proveedores = relationship("UsuarioProveedor", back_populates="Usuario")

class Proveedor(Base):
    __tablename__ = 'Proveedor'
    
    IdProveedor = Column(Integer, primary_key=True, autoincrement=True)
    IdTipoProveedor = Column(Integer, ForeignKey('TipoProveedor.IdTipoProveedor'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    UrlLogo = Column(String(300), nullable=False)
    UrlPaginaWeb = Column(String(300), nullable=True)
    EnvioDomicilio = Column(Boolean, nullable=True)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
    TipoProveedor = relationship("TipoProveedor", back_populates="Proveedores")
    Listas = relationship("Lista", back_populates="Proveedor")
    Productos = relationship("ProductoProveedor", back_populates="Proveedor")
    Usuarios = relationship("UsuarioProveedor", back_populates="Proveedor")

class Producto(Base):
    __tablename__ = 'Producto'
    
    IdProducto = Column(Integer, primary_key=True, autoincrement=True)
    IdCategoria = Column(Integer, ForeignKey('Categoria.IdCategoria'), nullable=False)
    IdUnidadMedida = Column(Integer, ForeignKey('UnidadMedida.IdUnidadMedida'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    UrlImagen = Column(String(300), nullable=False)
    Descripcion = Column(String(300), nullable=True)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
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
    PrecioTotal = Column(Numeric(10, 2), nullable=False)
    FechaCreacion = Column(DateTime, default=lambda: datetime.now(pytz.timezone('America/La_Paz')))
    
    Usuario = relationship("Usuario", back_populates="Listas")
    Proveedor = relationship("Proveedor", back_populates="Listas")
    Productos = relationship("ListaProducto", back_populates="Lista")

class ListaProducto(Base):
    __tablename__ = 'ListaProducto'
    
    IdLista = Column(Integer, ForeignKey('Lista.IdLista'), primary_key=True)
    IdProducto = Column(Integer, ForeignKey('Producto.IdProducto'), primary_key=True)
    PrecioActual = Column(Numeric(10, 2), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    
    Lista = relationship("Lista", back_populates="Productos")
    Producto = relationship("Producto", back_populates="Listas")

class UsuarioProveedor(Base):
    __tablename__ = 'UsuarioProveedor'
    
    IdProveedor = Column(Integer, ForeignKey('Proveedor.IdProveedor'), primary_key=True)
    IdUsuario = Column(Integer, ForeignKey('Usuario.IdUsuario'), primary_key=True)
    ProductosComprados = Column(Integer, nullable=False)
    FechaUltimaCompra = Column(DateTime, nullable=False)
    Preferencia = Column(Boolean, nullable=False)
    
    Proveedor = relationship("Proveedor", back_populates="Usuarios")
    Usuario = relationship("Usuario", back_populates="Proveedores")

class ProductoProveedor(Base):
    __tablename__ = 'ProductoProveedor'
    
    IdProducto = Column(Integer, ForeignKey('Producto.IdProducto'), primary_key=True)
    IdProveedor = Column(Integer, ForeignKey('Proveedor.IdProveedor'), primary_key=True)
    Precio = Column(Numeric(10, 2), nullable=False)
    PrecioOferta = Column(Numeric(10, 2), nullable=True)
    DescripcionOferta = Column(String(200), nullable=True, default="No habia oferta")
    FechaOferta = Column(DateTime, nullable=False)
    FechaPrecio = Column(DateTime, nullable=False)
    
    Producto = relationship("Producto", back_populates="Proveedores")
    Proveedor = relationship("Proveedor", back_populates="Productos")
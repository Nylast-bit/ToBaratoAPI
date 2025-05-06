from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship, declarative_base
from app.database import Base
from app.utils import now_bolivia

class TipoUsuario(Base):
    __tablename__ = 'TipoUsuario'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    NombreTipoUsuario = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Usuarios = relationship("Usuario", back_populates="TipoUsuario")

class TipoProveedor(Base):
    __tablename__ = 'TipoProveedor'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Proveedores = relationship("Proveedor", back_populates="TipoProveedor")

class Categoria(Base):
    __tablename__ = 'Categoria'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Productos = relationship("Producto", back_populates="Categoria")

class UnidadMedida(Base):
    __tablename__ = 'UnidadMedida'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(100), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Productos = relationship("Producto", back_populates="UnidadMedida")

class Usuario(Base):
    __tablename__ = 'Usuario'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    TipoUsuarioId = Column(Integer, ForeignKey('TipoUsuario.Id'), nullable=False)
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
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    TipoProveedorId = Column(Integer, ForeignKey('TipoProveedor.Id'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    UrlLogo = Column(Text, nullable=False)
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
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    ProveedorId = Column(Integer, ForeignKey('Proveedor.Id'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    Latitud = Column(String(50), nullable=False)
    Longitud = Column(String(50), nullable=False)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Proveedor = relationship("Proveedor", back_populates="Sucursales")
    UsuarioProveedores = relationship("UsuarioProveedor", back_populates="Sucursal")

class Producto(Base):
    __tablename__ = 'Producto'
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    CategoriaId = Column(Integer, ForeignKey('Categoria.Id'), nullable=False)
    UnidadMedidaId = Column(Integer, ForeignKey('UnidadMedida.Id'), nullable=False)
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
    
    Id = Column(Integer, primary_key=True, autoincrement=True)
    UsuarioId = Column(Integer, ForeignKey('Usuario.Id'), nullable=False)
    ProveedorId = Column(Integer, ForeignKey('Proveedor.Id'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    PrecioTotal = Column(Numeric(10, 2), nullable=False, default=0.00)
    FechaCreacion = Column(DateTime, default=now_bolivia)
    
    Usuario = relationship("Usuario", back_populates="Listas")
    Proveedor = relationship("Proveedor", back_populates="Listas")
    Productos = relationship("ListaProducto", back_populates="Lista")

class ListaProducto(Base):
    __tablename__ = 'ListaProducto'
    __table_args__ = (
        PrimaryKeyConstraint('ListaId', 'ProductoId'),
        ForeignKeyConstraint(['ListaId'], ['Lista.Id']),
        ForeignKeyConstraint(['ProductoId'], ['Producto.Id']),
    )
    
    ListaId = Column(Integer)
    ProductoId = Column(Integer)
    PrecioActual = Column(Numeric(10, 2), nullable=False)
    Cantidad = Column(Integer, nullable=False, default=1)
    
    Lista = relationship("Lista", back_populates="Productos")
    Producto = relationship("Producto", back_populates="Listas")

class UsuarioProveedor(Base):
    __tablename__ = 'UsuarioProveedor'
    __table_args__ = (
        PrimaryKeyConstraint('ProveedorId', 'UsuarioId'),
    )
    
    ProveedorId = Column(Integer, ForeignKey('Proveedor.Id'))
    UsuarioId = Column(Integer, ForeignKey('Usuario.Id'))
    SucursalId = Column(Integer, ForeignKey('Sucursal.Id'), nullable=False)
    ProductosComprados = Column(Integer, nullable=False, default=0)
    FechaUltimaCompra = Column(DateTime)
    Preferencia = Column(Boolean, nullable=False, default=False)
    
    Proveedor = relationship("Proveedor", back_populates="Usuarios")
    Usuario = relationship("Usuario", back_populates="Proveedores")
    Sucursal = relationship("Sucursal", back_populates="UsuarioProveedores")

class ProductoProveedor(Base):
    __tablename__ = 'ProductoProveedor'
    __table_args__ = (
        PrimaryKeyConstraint('ProductoId', 'ProveedorId'),
    )
    
    ProductoId = Column(Integer, ForeignKey('Producto.Id'))
    ProveedorId = Column(Integer, ForeignKey('Proveedor.Id'))
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
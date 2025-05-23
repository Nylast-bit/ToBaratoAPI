from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import UsuarioProveedor, Proveedor, Usuario
from app.schemas.usuarioproveedor import UsuarioProveedorCreate, UsuarioProveedorResponse, UsuarioProveedorUpdate
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

from sqlalchemy import select

@router.post("/usuarioproveedor", response_model=UsuarioProveedorResponse)
async def crear_usuarioproveedor(
    usuarioProveedorParam: UsuarioProveedorCreate,
    db: AsyncSession = Depends(get_db)
):
    # Validar que el usuario exista
    result_usuario = await db.execute(
        select(Usuario).where(Usuario.IdUsuario == usuarioProveedorParam.IdUsuario)
    )
    usuario = result_usuario.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar que el proveedor exista
    result_proveedor = await db.execute(
        select(Proveedor).where(Proveedor.IdProveedor == usuarioProveedorParam.IdProveedor)
    )
    proveedor = result_proveedor.scalar_one_or_none()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    # Crear el nuevo registro
    nuevo_usuarioproveedor = UsuarioProveedor(
        IdProveedor=usuarioProveedorParam.IdProveedor,
        IdUsuario=usuarioProveedorParam.IdUsuario,
        ProductosComprados=usuarioProveedorParam.ProductosComprados,
        FechaUltimaCompra=usuarioProveedorParam.FechaUltimaCompra,
        Preferencia=usuarioProveedorParam.Preferencia,
    )
    db.add(nuevo_usuarioproveedor)
    await db.commit()
    await db.refresh(nuevo_usuarioproveedor)
    return nuevo_usuarioproveedor





# Obtener todos los productos
@router.get("/usuarioproveedor", response_model=List[UsuarioProveedorResponse])
async def obtener_usuarioproveedor(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UsuarioProveedor))
    usuarioproveedor = result.scalars().all()
    return usuarioproveedor


# Obtener un usuario proveedor por IdUsuario y IdProveedor
@router.get("/usuarios/{id_usuario}/proveedores/{id_proveedor}", response_model=list[UsuarioProveedorResponse])
async def obtener_usuarioproveedor_por_usuario_y_proveedor(
    id_usuario: int,
    id_proveedor: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UsuarioProveedor).where(
            UsuarioProveedor.IdUsuario == id_usuario,
            UsuarioProveedor.IdProveedor == id_proveedor
        )
    )
    usuarioproveedores = result.scalars().all()
    if not usuarioproveedores:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return usuarioproveedores


#Obtener usuario proveedor por su id
@router.get("/usuarioproveedor/{id}", response_model=UsuarioProveedorResponse)
async def obtener_usuarioproveedor_por_id(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UsuarioProveedor).where(UsuarioProveedor.IdUsuarioProveedor == id)
    )
    usuarioproveedor = result.scalar_one_or_none()
    if not usuarioproveedor:
        raise HTTPException(status_code=404, detail="UsuarioProveedor no encontrado")
    return usuarioproveedor

#buscar todas las compras de un usuario por su id
@router.get("/usuariocompras/{id_usuario}", response_model=list[UsuarioProveedorResponse])
async def obtener_compras_por_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UsuarioProveedor).where(UsuarioProveedor.IdUsuario == id_usuario)
    )
    compras = result.scalars().all()
    
    if not compras:
        raise HTTPException(status_code=404, detail="No se encontraron compras para el usuario")
    
    return compras

#buscar todas las ventas de un proveedor por su id
@router.get("/proveedorventas/{id_proveedor}", response_model=list[UsuarioProveedorResponse])
async def obtener_ventas_por_proveedor(
    id_proveedor: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UsuarioProveedor).where(UsuarioProveedor.IdProveedor == id_proveedor)
    )
    ventas = result.scalars().all()

    if not ventas:
        raise HTTPException(status_code=404, detail="No se encontraron ventas para el proveedor")

    return ventas


#actualizar un usuarioproveedor por ID
@router.put("/usuarioproveedor/{id_usuarioproveedor}", response_model=UsuarioProveedorResponse)
async def actualizar_usuario_proveedor_por_id(
    id_usuarioproveedor: int,
    datos: UsuarioProveedorUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza una relación Usuario-Proveedor por IdUsuarioProveedor (asincrónica)
    """
    # 1. Buscar la relación existente por ID
    result = await db.execute(
        select(UsuarioProveedor).where(UsuarioProveedor.IdUsuarioProveedor == id_usuarioproveedor)
    )
    relacion = result.scalar_one_or_none()

    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "IdUsuarioProveedor": id_usuarioproveedor
            }
        )

    try:
        # 2. Validar y procesar datos
        update_data = datos.model_dump(exclude_unset=True)
        
        if "ProductosComprados" in update_data and update_data["ProductosComprados"] < 0:
            raise ValueError("Los productos comprados no pueden ser negativos")
        
        # 3. Aplicar la actualización
        for campo, valor in update_data.items():
            setattr(relacion, campo, valor)

        await db.commit()
        await db.refresh(relacion)
        return relacion

    except ValueError as ve:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "message": str(ve)
            }
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al actualizar relación",
                "details": str(e)
            }
        )


#Eliminar un producto
@router.delete("/usuarioproveedor/{id_usuarioproveedor}", response_model=UsuarioProveedorResponse)
async def eliminar_relacion_por_id(
    id_usuarioproveedor: int,
    db: AsyncSession = Depends(get_db)
):
    # 1. Buscar la relación existente por IdUsuarioProveedor
    result = await db.execute(
        select(UsuarioProveedor).where(UsuarioProveedor.IdUsuarioProveedor == id_usuarioproveedor)
    )
    relacion = result.scalar_one_or_none()

    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "IdUsuarioProveedor": id_usuarioproveedor
            }
        )

    # 2. Eliminar la relación
    await db.delete(relacion)
    await db.commit()

    # 3. Devolver el elemento eliminado
    return relacion

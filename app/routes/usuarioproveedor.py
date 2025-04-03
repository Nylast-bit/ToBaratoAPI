from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import UsuarioProveedor
from app.database import SessionLocal
from app.schemas.usuarioproveedor import UsuarioProveedorCreate, UsuarioProveedorResponse, UsuarioProveedorUpdate


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear un nueva unidad de medida
@router.post("/usuarioproveedor", response_model=UsuarioProveedorResponse)
def crear_listaproducto(usuarioProveedorParam: UsuarioProveedorCreate, db: Session = Depends(get_db)):
    nuevo_usuarioproveedor= UsuarioProveedor(
        IdProveedor = usuarioProveedorParam.IdProveedor, # ← Usa el nombre correcto
        IdUsuario = usuarioProveedorParam.IdUsuario, # ← Usa el nombre correcto 
        ProductosComprados = usuarioProveedorParam.ProductosComprados, # ← Usa el nombre correcto
        FechaUltimaCompra = usuarioProveedorParam.FechaUltimaCompra, # ← Usa el nombre correcto
        Preferencia = usuarioProveedorParam.Preferencia, # ← Usa el nombre correcto


    )
    db.add(nuevo_usuarioproveedor)
    db.commit()
    db.refresh(nuevo_usuarioproveedor)
    return nuevo_usuarioproveedor


# Obtener todos los productos
@router.get("/usuarioproveedor", response_model=List[UsuarioProveedorResponse])
def obtener_usuarioproveedor(db: Session = Depends(get_db)):
    usuarioproveedor = db.query(UsuarioProveedor).all()
    if not usuarioproveedor:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return usuarioproveedor


@router.put("/usuarios/{id_usuario}/proveedores/{id_proveedor}", response_model=UsuarioProveedorResponse)
def actualizar_usuario_proveedor(
    id_usuario: int,
    id_proveedor: int,
    datos: UsuarioProveedorUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la relación entre un usuario y un proveedor
    """
    # 1. Buscar la relación existente
    relacion = db.query(UsuarioProveedor).filter(
        UsuarioProveedor.IdUsuario == id_usuario,
        UsuarioProveedor.IdProveedor == id_proveedor
    ).first()
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "IdUsuario": id_usuario,
                "IdProveedor": id_proveedor
            }
        )

    try:
        # 2. Validar y procesar datos
        update_data = datos.model_dump(exclude_unset=True)
        
        if "ProductosComprados" in update_data and update_data["ProductosComprados"] < 0:
            raise ValueError("Los productos comprados no pueden ser negativos")
        
        # 3. Aplicar actualización
        for campo, valor in update_data.items():
            setattr(relacion, campo, valor)
        
        db.commit()
        db.refresh(relacion)
        return relacion

    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "message": str(ve)
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al actualizar relación",
                "details": str(e)
            }
        )

#Eliminar un producto
@router.delete("/usuarios/{id_usuario}/proveedores/{id_proveedor}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_relacion(id_usuario: int, id_proveedor: int, db: Session = Depends(get_db)):
    relacion = db.query(UsuarioProveedor).filter(
        UsuarioProveedor.IdUsuario == id_usuario,
        UsuarioProveedor.IdProveedor == id_proveedor
    ).first()
    
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    
    db.delete(relacion)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
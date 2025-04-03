from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import ListaProducto
from app.database import SessionLocal
from app.schemas.listaproductos import ListaProductoCreate, ListaProductoResponse, ListaProductoUpdate


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#Crear una nueva lista de productos
@router.post("/listaproducto", response_model=ListaProductoResponse)
def crear_listaproducto(listaProductoParam: ListaProductoCreate, db: Session = Depends(get_db)):
    nueva_listaproducto = ListaProducto(
        IdLista = listaProductoParam.IdLista, # ← Usa el nombre correcto
        IdProducto = listaProductoParam.IdProducto, # ← Usa el nombre correcto
        PrecioActual = listaProductoParam.PrecioActual, # ← Usa el nombre correcto
        Cantidad = listaProductoParam.Cantidad, # ← Usa el nombre correcto

    )
    db.add(nueva_listaproducto)
    db.commit()
    db.refresh(nueva_listaproducto)
    return nueva_listaproducto

# Obtener todos las listas de productos
@router.get("/listaproducto", response_model=List[ListaProductoResponse])   
def obtener_listaproductos(db: Session = Depends(get_db)):
    listaproductos = db.query(ListaProducto).all()
    if not listaproductos:
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return listaproductos

# Obtener una lista de productos por ID
@router.get("/listas/{id_lista}/productos/{id_producto}", response_model=ListaProductoResponse)
def obtener_producto_lista(
    id_lista: int,
    id_producto: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un producto específico de una lista por sus IDs compuestos
    """
    relacion = db.query(ListaProducto).filter(
        ListaProducto.IdLista == id_lista,
        ListaProducto.IdProducto == id_producto
    ).first()
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "IdLista": id_lista,
                "IdProducto": id_producto
            }
        )
    
    return relacion

#Actualizar un producto
@router.put("/listas/{id_lista}/productos/{id_producto}", response_model=ListaProductoResponse)
def actualizar_producto_lista(
    id_lista: int,
    id_producto: int,
    datos: ListaProductoUpdate,
    db: Session = Depends(get_db)
):
    relacion = db.query(ListaProducto).filter(
        ListaProducto.IdLista == id_lista,
        ListaProducto.IdProducto == id_producto
    ).first()
    
    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    
    update_data = datos.model_dump(exclude_unset=True)
    
    for campo, valor in update_data.items():
        setattr(relacion, campo, valor)
    
    db.commit()
    db.refresh(relacion)
    return relacion
   

#eliminar un producto de una lista
@router.delete("/listas/{id_lista}/productos/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto_lista(
    id_lista: int,
    id_producto: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un producto de una lista usando los IDs compuestos
    """
    relacion = db.query(ListaProducto).filter(
        ListaProducto.IdLista == id_lista,
        ListaProducto.IdProducto == id_producto
    ).first()
    
    if not relacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Relación no encontrada",
                "IdLista": id_lista,
                "IdProducto": id_producto
            }
        )
    
    try:
        db.delete(relacion)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al eliminar relación",
                "details": str(e)
            }
        )
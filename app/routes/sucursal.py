from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import Sucursal, Proveedor, ProductoProveedor
from app.schemas.sucursal import SucursalCreate, SucursalResponse, SucursalUpdate, UbicacionProductoRequest, ProductoSucursalResponse, RutaProveedoresRequest
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from sqlalchemy import func
from geopy.distance import geodesic
from decimal import Decimal



router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/sucursalprueba")
def test_sucursal():
    return {"msg": "todo bien con sucursal"}

# Crear una nueva sucursal
@router.post("/sucursal", response_model=SucursalResponse, status_code=status.HTTP_201_CREATED)
async def crear_sucursal(sucursal: SucursalCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Verificar que el proveedor exista
        result = await db.execute(select(Proveedor).where(Proveedor.IdProveedor == sucursal.IdProveedor))
        proveedor = result.scalar_one_or_none()
        if proveedor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Proveedor no válido",
                    "code": "INVALID_PROVIDER",
                    "field": "IdProveedor",
                    "value": sucursal.IdProveedor
                }
            )

        # Validar que no exista ya una sucursal con el mismo nombre para el mismo proveedor
        result = await db.execute(
            select(Sucursal).where(
                Sucursal.NombreSucursal == sucursal.NombreSucursal,
                Sucursal.IdProveedor == sucursal.IdProveedor
            )
        )
        sucursal_existente = result.scalar_one_or_none()
        if sucursal_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Ya existe una sucursal con ese nombre para el proveedor especificado",
                    "code": "DUPLICATE_BRANCH",
                    "field": "NombreSucursal",
                    "value": sucursal.NombreSucursal
                }
            )


        # Crear y guardar la nueva sucursal
        nueva_sucursal = Sucursal(
            IdProveedor=sucursal.IdProveedor,
            NombreSucursal=sucursal.NombreSucursal,
            Latitud=sucursal.latitud,
            Longitud=sucursal.longitud,
            FechaCreacion=datetime.now().replace(tzinfo=None)
        )
        db.add(nueva_sucursal)
        await db.commit()
        await db.refresh(nueva_sucursal)

        return nueva_sucursal

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al crear sucursal",
                "code": "SUCURSAL_CREATION_ERROR",
                "details": str(e)
            }   
        )
    
# Obtener todas las sucursales
@router.get("/sucursal", response_model=List[SucursalResponse])
async def obtener_sucursales(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Sucursal))
        sucursales = result.scalars().all()

        if not sucursales:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron sucursales"
            )

        return sucursales

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las sucursales: {str(e)}"
        )


# Obtener una sucursal por su ID
@router.get("/sucursal/{id}", response_model=SucursalResponse)
async def obtener_sucursal(id: int, db: Session = Depends(get_db)):
    # Validación del ID
    if id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El ID de la sucursal debe ser un número positivo", "id": id}
        )

    try:
        sucursal = db.query(Sucursal).filter(Sucursal.IdSucursal == id).first()
        
        if not sucursal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Sucursal no encontrada", "id": id}
            )
        
        return sucursal
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la sucursal: {str(e)}"
        )


# Actualizar una sucursal
@router.put("/sucursal/{id}", response_model=SucursalResponse)
async def actualizar_sucursal(id: int, sucursal_data: SucursalUpdate, db: AsyncSession = Depends(get_db)):
    try:
        # Buscar la sucursal asincrónicamente
        result = await db.execute(select(Sucursal).where(Sucursal.IdSucursal == id))
        sucursal = result.scalar_one_or_none()

        if not sucursal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Sucursal no encontrada", "id": id}
            )

        update_data = sucursal_data.model_dump(exclude_unset=True)

        # Validar que el proveedor exista si se está actualizando
        if "IdProveedor" in update_data:
            prov_result = await db.execute(select(Proveedor).where(Proveedor.IdProveedor == update_data["IdProveedor"]))
            proveedor = prov_result.scalar_one_or_none()
            if not proveedor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "El proveedor especificado no existe",
                        "field": "IdProveedor",
                        "value": update_data["IdProveedor"]
                    }
                )

        # Actualizar los campos
        for field, value in update_data.items():
            setattr(sucursal, field, value)

        await db.commit()
        await db.refresh(sucursal)

        return sucursal

    except HTTPException as http_ex:
        raise http_ex

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(ve)}
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al actualizar sucursal", "details": str(e)}
        )


# Eliminar una sucursal
@router.delete("/sucursal/{id}", response_model=SucursalResponse)
async def eliminar_sucursal(id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Buscar la sucursal asincrónicamente
        result = await db.execute(select(Sucursal).where(Sucursal.IdSucursal == id))
        sucursal = result.scalar_one_or_none()

        if not sucursal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Sucursal no encontrada", "id": id}
            )
        
        # Eliminar la sucursal
        await db.delete(sucursal)
        await db.commit()

        return sucursal

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al eliminar sucursal", "details": str(e)}
        )





@router.post("/sucursal-cercana", response_model=list[ProductoSucursalResponse])
async def obtener_producto_cercano(
    datos: UbicacionProductoRequest,
    db: AsyncSession = Depends(get_db)
):
    lat = datos.lat
    lng = datos.lng
    ids_productos = datos.ids_productos
    cantidades = datos.lista_cantidad

    if len(ids_productos) != len(cantidades):
        raise HTTPException(status_code=400, detail="La cantidad de productos no coincide con la cantidad de unidades")

    try:
        # 1. Obtener todas las sucursales
        result_sucursales = await db.execute(
            select(
                Sucursal.IdSucursal,
                Sucursal.NombreSucursal,
                Sucursal.Latitud,
                Sucursal.Longitud,
                Sucursal.IdProveedor
            )
        )
        sucursales = result_sucursales.all()

        if not sucursales:
            raise HTTPException(status_code=404, detail="No hay sucursales registradas")

        # 2. Calcular distancia a cada sucursal
        sucursales_con_distancia = []
        for s in sucursales:
            try:
                latitud = float(str(s.Latitud).replace(",", "").strip())
                longitud = float(str(s.Longitud).replace(",", "").strip())
                distancia = geodesic((lat, lng), (latitud, longitud)).km
            except Exception:
                continue

            sucursales_con_distancia.append({
                "IdSucursal": s.IdSucursal,
                "NombreSucursal": s.NombreSucursal,
                "Latitud": latitud,
                "Longitud": longitud,
                "IdProveedor": s.IdProveedor,
                "Distancia": distancia
            })

        if not sucursales_con_distancia:
            raise HTTPException(status_code=404, detail="No se pudo calcular la distancia a ninguna sucursal")

        # 3. Ordenar por cercanía
        sucursales_con_distancia.sort(key=lambda x: x["Distancia"])

        # 4. Filtrar: solo una sucursal por proveedor
        proveedor_visto = set()
        sucursales_filtradas = []
        for suc in sucursales_con_distancia:
            if suc["IdProveedor"] not in proveedor_visto:
                proveedor_visto.add(suc["IdProveedor"])
                sucursales_filtradas.append(suc)

        # 5. Calcular total por proveedor con cantidades
        resultados = []
        for suc in sucursales_filtradas:
            total = Decimal("0.0")
            precios_completos = True

            for idx, id_prod in enumerate(ids_productos):
                cantidad = cantidades[idx]

                result_precio = await db.execute(
                    select(ProductoProveedor.Precio).where(
                        ProductoProveedor.IdProveedor == suc["IdProveedor"],
                        ProductoProveedor.IdProducto == id_prod
                    )
                )
                precio_unitario = result_precio.scalar()
                if precio_unitario is None:
                    precios_completos = False
                    break

                total += precio_unitario * cantidad

            if precios_completos:
                resultados.append({
                    "NombreSucursal": suc["NombreSucursal"],
                    "Latitud": suc["Latitud"],
                    "Longitud": suc["Longitud"],
                    "IdProveedor": suc["IdProveedor"],
                    "Precio": float(round(total, 2)),
                    "Distancia": round(suc["Distancia"], 2)
                })

        if not resultados:
            raise HTTPException(status_code=204, detail="No hay proveedores que tengan todos los productos")

        # 6. Devolver los 3 más baratos
        resultados.sort(key=lambda x: x["Precio"])
        return resultados[:3]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener precios cercanos: {str(e)}")



@router.post("/ruta-multiples-listas")
async def obtener_sucursales_por_proveedor_mas_cercanas(
    datos: RutaProveedoresRequest,
    db: AsyncSession = Depends(get_db)
):
    lat = datos.lat
    lng = datos.lng
    ids_proveedores = list(dict.fromkeys(datos.ids_proveedores))  # ✅ eliminar duplicados

    if not ids_proveedores:
        raise HTTPException(status_code=400, detail="Debes proporcionar al menos un IdProveedor")

    try:
        # 1. Obtener todas las sucursales de los proveedores dados
        result = await db.execute(
            select(
                Sucursal.IdSucursal,
                Sucursal.NombreSucursal,
                Sucursal.Latitud,
                Sucursal.Longitud,
                Sucursal.IdProveedor
            ).where(Sucursal.IdProveedor.in_(ids_proveedores))
        )
        sucursales = result.all()

        if not sucursales:
            raise HTTPException(status_code=404, detail="No se encontraron sucursales para los proveedores dados")

        # 2. Calcular distancia a cada sucursal
        sucursales_con_distancia = []
        for s in sucursales:
            try:
                latitud = float(str(s.Latitud).replace(",", "").strip())
                longitud = float(str(s.Longitud).replace(",", "").strip())
                distancia = geodesic((lat, lng), (latitud, longitud)).km
            except Exception:
                continue  # Si hay error de formato, ignoramos esa sucursal

            sucursales_con_distancia.append({
                "IdSucursal": s.IdSucursal,
                "NombreSucursal": s.NombreSucursal,
                "Latitud": latitud,
                "Longitud": longitud,
                "IdProveedor": s.IdProveedor,
                "Distancia": distancia
            })

        if not sucursales_con_distancia:
            raise HTTPException(status_code=404, detail="No se pudo calcular distancia a ninguna sucursal válida")

        # 3. Obtener la sucursal más cercana por proveedor
        sucursales_por_proveedor = {}
        for suc in sorted(sucursales_con_distancia, key=lambda x: x["Distancia"]):
            if suc["IdProveedor"] not in sucursales_por_proveedor:
                sucursales_por_proveedor[suc["IdProveedor"]] = suc

        # 4. Retornar lista de sucursales más cercanas
        return list(sucursales_por_proveedor.values())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar sucursales más cercanas: {str(e)}")

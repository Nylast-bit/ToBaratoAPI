from fastapi import APIRouter, Request
import subprocess
import json
from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from typing import List, Annotated
from app.models.models import ListaProducto
from app.schemas.listaproductos import ListaProductoCreate, ListaProductoResponse, ListaProductoUpdate
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, extract, desc
import google.generativeai as genai
import json
from sqlalchemy.future import select
import requests
from app.models.models import Producto, ListaProducto, Lista, Proveedor, Sucursal, Categoria
import os

router = APIRouter()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

db_dependency = Annotated[Session, Depends(get_db)]




GEMINI_API_KEY = "AIzaSyAtr1PnZ3sl8g26aw-gQVD-cqXJ2lxFNKw"
genai.configure(api_key=GEMINI_API_KEY)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def consultar_gemini(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception(f"Gemini API error: {response.status_code} -> {response.text}")

    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except KeyError:
        return "Error: La respuesta de Gemini no tiene el formato esperado."


@router.get("/dashboard/insights")
async def obtener_insights(db: AsyncSession = Depends(get_db)):
    insights = []

    # Productos más comprados por proveedor (con IDs)
    query1 = (
        select(
            Producto.IdProducto,
            Producto.Nombre,
            Proveedor.IdProveedor,
            Proveedor.Nombre,
            func.count().label("Total")
        )
        .join(ListaProducto, Producto.IdProducto == ListaProducto.IdProducto)
        .join(Lista, Lista.IdLista == ListaProducto.IdLista)
        .join(Proveedor, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Producto.IdProducto, Producto.Nombre, Proveedor.IdProveedor, Proveedor.Nombre)
        .order_by(desc("Total"))
        .limit(10)
    )
    result1 = await db.execute(query1)
    productos_comprados = [
        {
            "id_producto": r[0],
            "producto": r[1],
            "id_proveedor": r[2],
            "proveedor": r[3],
            "veces_comprado": r[4],
        } for r in result1
    ]
    insights.append({"Productos más comprados por proveedor": productos_comprados})

    # Días con más compras de productos (con detalles)
    query2 = (
        select(
            func.to_char(Lista.FechaCreacion, 'Day').label("dia_semana"),
            Producto.IdProducto,
            Producto.Nombre,
            func.count().label("total")
        )
        .join(ListaProducto, Lista.IdLista == ListaProducto.IdLista)
        .join(Producto, Producto.IdProducto == ListaProducto.IdProducto)
        .group_by("dia_semana", Producto.IdProducto, Producto.Nombre)
        .order_by(desc("total"))
        .limit(10)
    )
    result2 = await db.execute(query2)
    dias_populares = [
        {
            "dia": r[0].strip(),
            "id_producto": r[1],
            "producto": r[2],
            "compras": r[3]
        } for r in result2
    ]

    query2b = (
        select(Proveedor.Nombre, func.count(Lista.IdProveedor).label("total"))
        .join(Lista, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Proveedor.Nombre)
        .order_by(desc("total"))
        .limit(3)
    )
    result2b = await db.execute(query2b)
    proveedores_frecuentes = [r[0] for r in result2b]
    insights.append({"Días con más compras de productos": dias_populares, "Top 3 Proveedores más frecuentes": proveedores_frecuentes})

    # Tendencia semanal de compras con productos más frecuentes por semana
    sub_q = (
        select(
            func.date_trunc('week', Lista.FechaCreacion).label("semana"),
            Producto.IdProducto,
            Producto.Nombre,
            func.count().label("apariciones")
        )
        .join(ListaProducto, Lista.IdLista == ListaProducto.IdLista)
        .join(Producto, Producto.IdProducto == ListaProducto.IdProducto)
        .group_by("semana", Producto.IdProducto, Producto.Nombre)
    ).subquery()

    query5 = (
        select(
            sub_q.c.semana,
            sub_q.c.IdProducto,
            sub_q.c.Nombre,
            sub_q.c.apariciones
        )
        .order_by(sub_q.c.semana, desc(sub_q.c.apariciones))
    )
    result5 = await db.execute(query5)

    tendencias_semanales = {}
    for semana, id_prod, nombre_prod, apariciones in result5:
        key = semana.strftime("%Y-%m-%d")
        if key not in tendencias_semanales:
            tendencias_semanales[key] = []
        tendencias_semanales[key].append({
            "id_producto": id_prod,
            "producto": nombre_prod,
            "listas": apariciones
        })
    insights.append({"Tendencia semanal": tendencias_semanales})

    # Producto más comprado por categoría con distribución por proveedor
    query8 = (
        select(
            Categoria.NombreCategoria,
            Producto.IdProducto,
            Producto.Nombre,
            Proveedor.Nombre,
            func.count().label("Total")
        )
        .join(Producto, Categoria.IdCategoria == Producto.IdCategoria)
        .join(ListaProducto, Producto.IdProducto == ListaProducto.IdProducto)
        .join(Lista, Lista.IdLista == ListaProducto.IdLista)
        .join(Proveedor, Lista.IdProveedor == Proveedor.IdProveedor)
        .group_by(Categoria.NombreCategoria, Producto.IdProducto, Producto.Nombre, Proveedor.Nombre)
        .order_by(Categoria.NombreCategoria, desc("Total"))
    )
    result8 = await db.execute(query8)
    productos_categoria = {}
    for cat, id_prod, nombre_prod, proveedor, total in result8:
        if cat not in productos_categoria:
            productos_categoria[cat] = {
                "id_producto": id_prod,
                "producto": nombre_prod,
                "distribucion": []
            }
        if productos_categoria[cat]["producto"] == nombre_prod:
            productos_categoria[cat]["distribucion"].append({
                "proveedor": proveedor,
                "veces_comprado": total
            })
    insights.append({"Producto más comprado por categoría": productos_categoria})

    # Mapa de calor por hora del día (total representa la cantidad de listas creadas en esa hora)
    query9 = (
        select(extract('hour', Lista.FechaCreacion).label("hora"), func.count().label("total"))
        .group_by("hora")
        .order_by("hora")
    )
    result9 = await db.execute(query9)
    insights.append({"Mapa de calor por hora": [
        {"hora": int(r[0]), "total_listas_creadas": r[1]} for r in result9
    ]})

    return insights

@router.get("/dashboard/analizar-insights")
async def analizar_insights_con_ia(db: AsyncSession = Depends(get_db)):
    try:
        from .dashboard import obtener_insights  # si está en otro archivo, ajusta el import

        insights = await obtener_insights(db)

        prompt = f"""
        Eres un asesor de negocios experto. Este JSON contiene información sobre productos más comprados, días frecuentes, proveedores y tendencias.
        Da recomendaciones accionables para cada proveedor (ej: mejores días, productos más vendidos, horarios, promociones potenciales):

        {json.dumps(insights, indent=2)}
        """

        respuesta = consultar_gemini(prompt)
        return {"recomendaciones": respuesta}

    except Exception as e:
        return {"error": str(e)}
    

@router.post("/dashboard/analizar-pregunta")
async def analizar_pregunta(request: Request):
    body = await request.json()
    pregunta = body.get("pregunta")

    if not pregunta:
        return {"error": "Debes enviar una 'pregunta'."}

    try:
        respuesta = consultar_gemini(pregunta)
        return {"respuesta": respuesta}
    except Exception as e:
        return {"error": str(e)}
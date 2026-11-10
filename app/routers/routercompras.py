from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.compras import CompraCrear, CompraRespuesta
from app.services.servicio_compra import (
    listar_compras as listar_compras_servicio,
    crear_compra as crear_compra_servicio,
    obtener_compra as obtener_compra_servicio,
    cancelar_compra as cancelar_compra_servicio,
    listar_compras_por_fecha as listar_compras_por_fecha_servicio,
)
from app.security import requerir_admin


routercompra = APIRouter(prefix="/compras", tags=["Compras"])


@routercompra.get("/", response_model=list[CompraRespuesta])
def listar_compras(
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    return listar_compras_por_fecha_servicio(db, fecha_inicio, fecha_fin)


@routercompra.get("/{compra_id}", response_model=CompraRespuesta)
def obtener_compra(
    compra_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin),
):
    return obtener_compra_servicio(db, compra_id)


@routercompra.post("/", response_model=CompraRespuesta, status_code=201)
def registrar_compra(
    datos: CompraCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    return crear_compra_servicio(db, datos)


@routercompra.patch("/{compra_id}/cancelar", response_model=CompraRespuesta)
def cancelar_compra(
    compra_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin),
):
    return cancelar_compra_servicio(db, compra_id)
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.infoventas import VentaCrear, VentaRespuesta
from app.services.servicio_venta import (
    listar_ventas as listar_ventas_servicio,
    obtener_venta as obtener_venta_servicio,
    crear_venta as crear_venta_servicio,
    cancelar_venta as cancelar_venta_servicio,
    listar_ventas_por_fecha as listar_ventas_por_fecha_servicio,
)
from app.security import obtener_usuario_actual


routerventa = APIRouter(prefix="/ventas", tags=["Ventas"])


@routerventa.get("/", response_model=list[VentaRespuesta])
def listar_ventas(
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    return listar_ventas_por_fecha_servicio(db, fecha_inicio, fecha_fin)


@routerventa.get("/reporte", response_model=list[VentaRespuesta])
def reporte_ventas(
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual),
):
    return listar_ventas_por_fecha_servicio(db, fecha_inicio, fecha_fin)


@routerventa.get("/{venta_id}", response_model=VentaRespuesta)
def obtener_venta(
    venta_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    return obtener_venta_servicio(db, venta_id)


@routerventa.post("/", response_model=VentaRespuesta, status_code=201)
def registrar_venta(
    datos: VentaCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    return crear_venta_servicio(db, datos)


@routerventa.patch("/{venta_id}/cancelar", response_model=VentaRespuesta)
def cancelar_venta(
    venta_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual),
):
    return cancelar_venta_servicio(db, venta_id)
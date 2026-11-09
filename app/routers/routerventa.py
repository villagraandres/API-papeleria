from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.infoventas import VentaCrear, VentaRespuesta
from app.services.servicio_venta import (
    listar_ventas as listar_ventas_servicio,
    obtener_venta as obtener_venta_servicio,
    crear_venta as crear_venta_servicio,
)
from app.security import obtener_usuario_actual


routerventa = APIRouter(prefix="/ventas", tags=["Ventas"])


@routerventa.get("/", response_model=list[VentaRespuesta])
def listar_ventas(
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    return listar_ventas_servicio(db)


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
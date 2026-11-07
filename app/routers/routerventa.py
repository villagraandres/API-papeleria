from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.models.venta import Venta
from app.schemas.infoventas import VentaCrear, VentaRespuesta
from app.services.sale_service import crear_venta
from app.security import obtener_usuario_actual


routerventa = APIRouter(prefix="/ventas", tags=["Ventas"])


@routerventa.get("/", response_model=list[VentaRespuesta])
def listar_ventas(
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    return db.query(Venta).all()


@routerventa.get("/{venta_id}", response_model=VentaRespuesta)
def obtener_venta(
    venta_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    venta = db.query(Venta).filter(
        Venta.id == venta_id
    ).first()

    if not venta:
        raise HTTPException(404, "Venta no encontrada")

    return venta


@routerventa.post("/", response_model=VentaRespuesta, status_code=201)
def registrar_venta(
    datos: VentaCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    return crear_venta(db, datos)
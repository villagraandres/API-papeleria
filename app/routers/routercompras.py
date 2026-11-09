from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.compras import CompraCrear, CompraRespuesta
from app.services.servicio_compra import (
    listar_compras as listar_compras_servicio,
    crear_compra as crear_compra_servicio,
)
from app.security import requerir_admin


routercompra = APIRouter(prefix="/compras", tags=["Compras"])


@routercompra.get("/", response_model=list[CompraRespuesta])
def listar_compras(
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    return listar_compras_servicio(db)


@routercompra.post("/", response_model=CompraRespuesta, status_code=201)
def registrar_compra(
    datos: CompraCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    return crear_compra_servicio(db, datos)
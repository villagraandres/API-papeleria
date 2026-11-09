from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.infocliente import ClienteCrear, ClienteRespuesta
from app.security import obtener_usuario_actual
from app.services.servicio_cliente import (
    listar_clientes as listar_clientes_servicio,
    crear_cliente as crear_cliente_servicio,
    eliminar_cliente as eliminar_cliente_servicio,
)


routercliente = APIRouter(prefix="/clientes", tags=["Clientes"])


@routercliente.get("/", response_model=list[ClienteRespuesta])
def listar_clientes(db: Session = Depends(obtener_bd)):
    return listar_clientes_servicio(db)


@routercliente.post("/", response_model=ClienteRespuesta, status_code=201)
def crear_cliente(
    datos: ClienteCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    return crear_cliente_servicio(db, datos)


@routercliente.delete("/{cliente_id}", status_code=204)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    eliminar_cliente_servicio(db, cliente_id)
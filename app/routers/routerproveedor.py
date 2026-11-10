from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.infoproveedor import ProveedorCrear, ProveedorRespuesta
from app.security import requerir_admin
from app.services.servicio_proveedor import (
    listar_proveedores as listar_proveedores_servicio,
    crear_proveedor as crear_proveedor_servicio,
    desactivar_proveedor as desactivar_proveedor_servicio,
    activar_proveedor as activar_proveedor_servicio,
)


routerproveedor = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@routerproveedor.get("/", response_model=list[ProveedorRespuesta])
def listar_proveedores(db: Session = Depends(obtener_bd)):
    return listar_proveedores_servicio(db)


@routerproveedor.post("/", response_model=ProveedorRespuesta, status_code=201)
def crear_proveedor(
    datos: ProveedorCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    return crear_proveedor_servicio(db, datos)


@routerproveedor.patch("/{proveedor_id}/desactivar", status_code=204)
def desactivar_proveedor(
    proveedor_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    desactivar_proveedor_servicio(db, proveedor_id)


@routerproveedor.patch("/{proveedor_id}/activar", status_code=204)
def activar_proveedor(
    proveedor_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin),
):
    activar_proveedor_servicio(db, proveedor_id)

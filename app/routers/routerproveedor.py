from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.models.proveedor import Proveedor
from app.schemas.infoproveedor import ProveedorCrear, ProveedorRespuesta
from app.security import obtener_usuario_actual, requerir_admin


routerproveedor = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@routerproveedor.get("/", response_model=list[ProveedorRespuesta])
def listar_proveedores(db: Session = Depends(obtener_bd)):
    return db.query(Proveedor).all()


@routerproveedor.post("/", response_model=ProveedorRespuesta, status_code=201)
def crear_proveedor(
    datos: ProveedorCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    proveedor = Proveedor(**datos.model_dump())

    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)

    return proveedor


@routerproveedor.delete("/{proveedor_id}", status_code=204)
def eliminar_proveedor(
    proveedor_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    proveedor = db.query(Proveedor).filter(
        Proveedor.id == proveedor_id
    ).first()

    if not proveedor:
        raise HTTPException(404, "Proveedor no encontrado")

    db.delete(proveedor)
    db.commit()
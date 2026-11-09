from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.proveedor import Proveedor
from app.repositories import repositorio_base
from app.schemas.infoproveedor import ProveedorCrear


def listar_proveedores(db: Session) -> list[Proveedor]:
    return db.query(Proveedor).all()


def crear_proveedor(db: Session, datos: ProveedorCrear) -> Proveedor:
    proveedor = Proveedor(**datos.model_dump())
    return repositorio_base.guardar(db, proveedor)


def eliminar_proveedor(db: Session, proveedor_id: int) -> None:
    proveedor = db.query(Proveedor).filter(
        Proveedor.id == proveedor_id
    ).first()

    if not proveedor:
        raise HTTPException(404, "Proveedor no encontrado")

    db.delete(proveedor)
    db.commit()

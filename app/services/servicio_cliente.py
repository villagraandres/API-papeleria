from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories import repositorio_base
from app.schemas.infocliente import ClienteCrear


def listar_clientes(db: Session) -> list[Cliente]:
    return db.query(Cliente).all()


def crear_cliente(db: Session, datos: ClienteCrear) -> Cliente:
    if datos.correo and db.query(Cliente).filter(
        Cliente.correo == datos.correo
    ).first():
        raise HTTPException(400, "El correo ya está registrado")

    cliente = Cliente(**datos.model_dump())
    return repositorio_base.guardar(db, cliente)


def eliminar_cliente(db: Session, cliente_id: int) -> None:
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")

    db.delete(cliente)
    db.commit()

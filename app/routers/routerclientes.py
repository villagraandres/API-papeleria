from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.models.cliente import Cliente
from app.schemas.infocliente import ClienteCrear, ClienteRespuesta
from app.security import obtener_usuario_actual


routercliente = APIRouter(prefix="/clientes", tags=["Clientes"])


@routercliente.get("/", response_model=list[ClienteRespuesta])
def listar_clientes(db: Session = Depends(obtener_bd)):
    return db.query(Cliente).all()


@routercliente.post("/", response_model=ClienteRespuesta, status_code=201)
def crear_cliente(
    datos: ClienteCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    if datos.correo and db.query(Cliente).filter(
        Cliente.correo == datos.correo
    ).first():
        raise HTTPException(400, "El correo ya está registrado")

    cliente = Cliente(**datos.model_dump())

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente


@routercliente.delete("/{cliente_id}", status_code=204)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(obtener_usuario_actual)
):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")

    cliente.correo = None
    db.delete(cliente)
    db.commit()
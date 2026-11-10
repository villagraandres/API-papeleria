from sqlalchemy.orm import Session
from app.models.producto import Producto


def listar_productos(db: Session):
    return db.query(Producto).all()


def obtener_producto(db: Session, producto_id: int):
    return db.query(Producto).filter(
        Producto.id == producto_id
    ).first()


def crear_producto(db: Session, producto: Producto):
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto

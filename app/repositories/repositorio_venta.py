from sqlalchemy.orm import Session
from app.models.venta import Venta


def listar_ventas(db: Session):
    return db.query(Venta).all()


def obtener_venta(db: Session, venta_id: int):
    return db.query(Venta).filter(
        Venta.id == venta_id
    ).first()
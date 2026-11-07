from sqlalchemy.orm import Session
from app.models.venta import Venta


def get_all_sales(db: Session):
    return db.query(Venta).all()


def get_sale(db: Session, sale_id: int):
    return db.query(Venta).filter(
        Venta.id == sale_id
    ).first()
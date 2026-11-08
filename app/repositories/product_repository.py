from sqlalchemy.orm import Session
from app.models.producto import Producto


def get_all_products(db: Session):
    return db.query(Producto).all()


def get_product(db: Session, product_id: int):
    return db.query(Producto).filter(
        Producto.id == product_id
    ).first()


def create_product(db: Session, product: Producto):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Producto):
    db.delete(product)
    db.commit()
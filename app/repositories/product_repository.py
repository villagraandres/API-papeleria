from sqlalchemy.orm import Session
from app.models.producto import Productos


def get_all_products(db: Session):
    return db.query(Productos).all()


def get_product(db: Session, product_id: int):
    return db.query(Productos).filter(
        Productos.id == product_id
    ).first()


def create_product(db: Session, product: Productos):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Productos):
    db.delete(product)
    db.commit()
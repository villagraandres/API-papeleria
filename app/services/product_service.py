from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.producto import Product
from app.models.categoria import Categoria as Category


def create_product(db: Session, data):

    category = db.query(Category).filter(
        Category.id == data.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="La categoría no existe"
        )

    product = Product(**data.model_dump())

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def update_product(db: Session, product_id: int, data):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    changes = data.model_dump(exclude_unset=True)

    if "category_id" in changes:
        category = db.query(Category).filter(
            Category.id == changes["category_id"]
        ).first()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="La categoría no existe"
            )

    for key, value in changes.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return product
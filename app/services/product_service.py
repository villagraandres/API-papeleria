from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.producto import Producto
from app.models.categoria import Categoria


def crear_producto(db: Session, datos):

    categoria = db.query(Categoria).filter(
        Categoria.id == datos.categoria_id
    ).first()

    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="La categoría no existe"
        )

    producto = Producto(**datos.model_dump())

    db.add(producto)
    db.commit()
    db.refresh(producto)

    return producto


def actualizar_producto(db: Session, producto_id: int, datos):

    producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    changes = datos.model_dump(exclude_unset=True)

    if "categoria_id" in changes:
        categoria = db.query(Categoria).filter(
            Categoria.id == changes["categoria_id"]
        ).first()

        if not categoria:
            raise HTTPException(
                status_code=404,
                detail="La categoría no existe"
            )

    for key, value in changes.items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)

    return producto
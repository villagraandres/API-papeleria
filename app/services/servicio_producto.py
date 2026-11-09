from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.producto import Producto
from app.models.categoria import Categoria
from app.repositories import repositorio_base
from app.schemas.productos import ProductoCrear, ProductoActualizar


def listar_productos(db: Session) -> list[Producto]:
    return db.query(Producto).all()


def obtener_producto(db: Session, producto_id: int) -> Producto:
    producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()

    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    return producto


def crear_producto(db: Session, datos: ProductoCrear) -> Producto:

    categoria = db.query(Categoria).filter(
        Categoria.id == datos.categoria_id
    ).first()

    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="La categoría no existe"
        )

    producto = Producto(**datos.model_dump())

    return repositorio_base.guardar(db, producto)


def actualizar_producto(
    db: Session,
    producto_id: int,
    datos: ProductoActualizar
) -> Producto:

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


def eliminar_producto(db: Session, producto_id: int) -> None:
    producto = obtener_producto(db, producto_id)
    db.delete(producto)
    db.commit()
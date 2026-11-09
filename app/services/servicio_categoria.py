from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.producto import Producto
from app.repositories import repositorio_base
from app.schemas.categorias import CategoriaCrear


def listar_categorias(db: Session) -> list[Categoria]:
    return db.query(Categoria).all()


def crear_categoria(db: Session, datos: CategoriaCrear) -> Categoria:
    existente = db.query(Categoria).filter(
        Categoria.nombre == datos.nombre
    ).first()

    if existente:
        raise HTTPException(400, "La categoría ya existe")

    categoria = Categoria(**datos.model_dump())
    return repositorio_base.guardar(db, categoria)


def eliminar_categoria(db: Session, categoria_id: int) -> None:
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")

    producto_asociado = db.query(Producto).filter(
        Producto.categoria_id == categoria_id
    ).first()

    if producto_asociado:
        raise HTTPException(409, "La categoría tiene productos asociados")

    db.delete(categoria)
    db.commit()

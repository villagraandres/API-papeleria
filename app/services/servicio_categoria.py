from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.producto import Producto
from app.repositories import repositorio_base
from app.schemas.categorias import CategoriaCrear


def listar_categorias(db: Session) -> list[Categoria]:
    return db.query(Categoria).filter(Categoria.activo.is_(True)).all()


def crear_categoria(db: Session, datos: CategoriaCrear) -> Categoria:
    existente = db.query(Categoria).filter(
        Categoria.nombre == datos.nombre
    ).first()

    if existente:
        raise HTTPException(400, "La categoría ya existe")

    categoria = Categoria(**datos.model_dump())
    categoria.activo = True
    return repositorio_base.guardar(db, categoria)


def desactivar_categoria(db: Session, categoria_id: int) -> None:
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")

    categoria.activo = False
    db.commit()


def activar_categoria(db: Session, categoria_id: int) -> None:
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")
    categoria.activo = True
    db.commit()

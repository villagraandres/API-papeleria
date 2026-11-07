from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.models.categoria import Categoria
from app.schemas.categorias import CategoriaCrear, CategoriaRespuesta
from app.security import requerir_admin


routercategoria = APIRouter(prefix="/categorias", tags=["Categorías"])


@routercategoria.get("/", response_model=list[CategoriaRespuesta])
def listar_categorias(db: Session = Depends(obtener_bd)):
    return db.query(Categoria).all()


@routercategoria.post("/", response_model=CategoriaRespuesta, status_code=201)
def crear_categoria(
    datos: CategoriaCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    existente = db.query(Categoria).filter(
        Categoria.nombre == datos.nombre
    ).first()

    if existente:
        raise HTTPException(400, "La categoría ya existe")

    categoria = Categoria(**datos.model_dump())

    db.add(categoria)
    db.commit()
    db.refresh(categoria)

    return categoria


@routercategoria.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if not categoria:
        raise HTTPException(404, "Categoría no encontrada")

    if db.query(__import__(
        "app.models.producto", fromlist=["Producto"]
    ).Producto).filter_by(categoria_id=categoria_id).first():
        raise HTTPException(409, "La categoría tiene productos asociados")

    db.delete(categoria)
    db.commit()
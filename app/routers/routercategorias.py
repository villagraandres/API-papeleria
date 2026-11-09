from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.categorias import CategoriaCrear, CategoriaRespuesta
from app.security import requerir_admin
from app.services.servicio_categoria import (
    listar_categorias as listar_categorias_servicio,
    crear_categoria as crear_categoria_servicio,
    eliminar_categoria as eliminar_categoria_servicio,
)


routercategoria = APIRouter(prefix="/categorias", tags=["Categorías"])


@routercategoria.get("/", response_model=list[CategoriaRespuesta])
def listar_categorias(db: Session = Depends(obtener_bd)):
    return listar_categorias_servicio(db)


@routercategoria.post("/", response_model=CategoriaRespuesta, status_code=201)
def crear_categoria(
    datos: CategoriaCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    return crear_categoria_servicio(db, datos)


@routercategoria.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    eliminar_categoria_servicio(db, categoria_id)
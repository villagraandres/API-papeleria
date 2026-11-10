from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.categorias import CategoriaCrear, CategoriaRespuesta
from app.security import requerir_admin
from app.services.servicio_categoria import (
    listar_categorias as listar_categorias_servicio,
    crear_categoria as crear_categoria_servicio,
    desactivar_categoria as desactivar_categoria_servicio,
    activar_categoria as activar_categoria_servicio,
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


@routercategoria.patch("/{categoria_id}/desactivar", status_code=204)
def desactivar_categoria(
    categoria_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):
    desactivar_categoria_servicio(db, categoria_id)


@routercategoria.patch("/{categoria_id}/activar", status_code=204)
def activar_categoria(
    categoria_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin),
):
    activar_categoria_servicio(db, categoria_id)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.productos import (
    ProductoCrear,
    ProductoActualizar,
    ProductoRespuesta
)
from app.services.servicio_producto import (
    listar_productos as listar_productos_servicio,
    obtener_producto as obtener_producto_servicio,
    crear_producto as crear_producto_servicio,
    actualizar_producto as actualizar_producto_servicio,
    desactivar_producto as desactivar_producto_servicio,
    activar_producto as activar_producto_servicio,
)
from app.security import obtener_usuario_actual, requerir_admin


routerproducto = APIRouter(prefix="/productos", tags=["Productos"])


@routerproducto.get("/", response_model=list[ProductoRespuesta])
def listar_productos(db: Session = Depends(obtener_bd)):
    return listar_productos_servicio(db)


@routerproducto.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener_producto(producto_id: int, db: Session = Depends(obtener_bd)):
    return obtener_producto_servicio(db, producto_id)


@routerproducto.post("/", response_model=ProductoRespuesta, status_code=201)
def agregar_producto(
    datos: ProductoCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):

    return crear_producto_servicio(db, datos)


@routerproducto.put("/{producto_id}", response_model=ProductoRespuesta)
def editar_producto(
    producto_id: int,
    datos: ProductoActualizar,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):

    return actualizar_producto_servicio(db, producto_id, datos)


@routerproducto.patch("/{producto_id}/desactivar", status_code=204)
def desactivar_producto(
    producto_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):

    desactivar_producto_servicio(db, producto_id)


@routerproducto.patch("/{producto_id}/activar", status_code=204)
def activar_producto(
    producto_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin),
):
    activar_producto_servicio(db, producto_id)
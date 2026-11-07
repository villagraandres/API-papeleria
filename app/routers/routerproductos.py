from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.models.producto import Producto
from app.schemas.productos import (
    ProductoCrear,
    ProductoActualizar,
    ProductoRespuesta
)
from app.services.product_service import (
    crear_producto,
    actualizar_producto
)
from app.security import obtener_usuario_actual, requerir_admin


routerproducto = APIRouter(prefix="/productos", tags=["Productos"])


@routerproducto.get("/", response_model=list[ProductoRespuesta])
def listar_productos(db: Session = Depends(obtener_bd)):

    return db.query(Producto).all()


@routerproducto.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener_producto(producto_id: int, db: Session = Depends(obtener_bd)):

    producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()

    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    return producto


@routerproducto.post("/", response_model=ProductoRespuesta, status_code=201)
def agregar_producto(
    datos: ProductoCrear,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):

    return crear_producto(db, datos)


@routerproducto.put("/{producto_id}", response_model=ProductoRespuesta)
def editar_producto(
    producto_id: int,
    datos: ProductoActualizar,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):

    return actualizar_producto(db, producto_id, datos)


@routerproducto.delete("/{producto_id}", status_code=204)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(obtener_bd),
    usuario=Depends(requerir_admin)
):

    producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()

    if not producto:
        raise HTTPException(404, "Producto no encontrado")

    db.delete(producto)
    db.commit()
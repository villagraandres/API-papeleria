from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.compra import Compra, PartidaCompra
from app.models.producto import Producto
from app.models.proveedor import Proveedor


def listar_compras(db: Session) -> list[Compra]:
    return db.query(Compra).all()


def crear_compra(db: Session, datos):

    try:
        proveedor = db.query(Proveedor).filter(
            Proveedor.id == datos.proveedor_id
        ).first()

        if not proveedor:
            raise HTTPException(
                status_code=404,
                detail="Proveedor no encontrado"
            )

        compra = Compra(
            proveedor_id=datos.proveedor_id,
            total=0
        )

        db.add(compra)
        db.flush()

        total = 0

        for item in datos.items:

            producto = db.query(Producto).filter(
                Producto.id == item.producto_id
            ).first()

            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item.producto_id} no encontrado"
                )

            subtotal = item.cantidad * item.costo_unitario

            item_compra = PartidaCompra(
                compra_id=compra.id,
                producto_id=producto.id,
                cantidad=item.cantidad,
                costo_unitario=item.costo_unitario,
                subtotal=subtotal
            )

            producto.stock += item.cantidad
            total += subtotal

            db.add(item_compra)

        compra.total = round(total, 2)

        db.commit()
        db.refresh(compra)

        return compra

    except Exception:
        db.rollback()
        raise
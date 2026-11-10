from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.compra import Compra, PartidaCompra
from app.models.producto import Producto
from app.models.proveedor import Proveedor


def listar_compras(db: Session) -> list[Compra]:
    return db.query(Compra).all()


def obtener_compra(db: Session, compra_id: int) -> Compra:
    compra = db.query(Compra).filter(Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(404, "Compra no encontrada")
    return compra


def listar_compras_por_fecha(
    db: Session,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
) -> list[Compra]:
    consulta = db.query(Compra)
    if fecha_inicio:
        consulta = consulta.filter(Compra.created_at >= fecha_inicio)
    if fecha_fin:
        consulta = consulta.filter(Compra.created_at <= fecha_fin)
    return consulta.order_by(Compra.created_at.desc()).all()


def crear_compra(db: Session, datos):

    try:
        proveedor = db.query(Proveedor).filter(
            Proveedor.id == datos.proveedor_id,
            Proveedor.activo.is_(True),
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
                Producto.id == item.producto_id,
                Producto.activo.is_(True),
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

        compra.iva = round(total * 0.16, 2)
        compra.total = round(total + compra.iva, 2)

        db.commit()
        db.refresh(compra)

        return compra

    except Exception:
        db.rollback()
        raise


def cancelar_compra(db: Session, compra_id: int) -> Compra:
    try:
        compra = obtener_compra(db, compra_id)
        if compra.estado == "cancelada":
            raise HTTPException(409, "La compra ya está cancelada")

        for item in compra.items:
            producto = db.query(Producto).filter(
                Producto.id == item.producto_id
            ).with_for_update().first()
            if not producto or producto.stock < item.cantidad:
                raise HTTPException(
                    409,
                    f"No se puede cancelar la compra: stock insuficiente para el producto {item.producto_id}",
                )
            producto.stock -= item.cantidad

        compra.estado = "cancelada"
        db.commit()
        db.refresh(compra)
        return compra
    except Exception:
        db.rollback()
        raise
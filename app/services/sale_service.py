from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.venta import Venta, PartidaVenta
from app.models.producto import Producto
from app.models.cliente import Cliente


def crear_venta(db: Session, datos):

    try:
        if datos.cliente_id is not None:
            customer = db.query(Cliente).filter(
                Cliente.id == datos.cliente_id
            ).first()

            if not customer:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

        venta = Venta(
            cliente_id=datos.cliente_id,
            total=0
        )

        db.add(venta)
        db.flush()

        total = 0

        for item in datos.items:

            producto = db.query(Producto).filter(
                Producto.id == item.producto_id
            ).with_for_update().first()

            if not producto:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item.producto_id} no encontrado"
                )

            if producto.stock < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, solicitado: {item.cantidad}"
                )

            subtotal = producto.precio * item.cantidad

            venta_item = PartidaVenta(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal
            )

            producto.stock -= item.cantidad
            total += subtotal

            db.add(venta_item)

        venta.total = round(total, 2)

        db.commit()
        db.refresh(venta)

        return venta

    except Exception:
        db.rollback()
        raise
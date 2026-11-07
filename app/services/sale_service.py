from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.venta import Venta, VentaItem
from app.models.producto import Productos
from app.models.cliente import Cliente


def create_sale(db: Session, data):

    try:
        if data.customer_id is not None:
            customer = db.query(Cliente).filter(
                Cliente.id == data.customer_id
            ).first()

            if not customer:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

        venta = Venta(
            customer_id=data.customer_id,
            total=0
        )

        db.add(venta)
        db.flush()

        total = 0

        for item in data.items:

            product = db.query(Productos).filter(
                Productos.id == item.product_id
            ).with_for_update().first()

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item.product_id} no encontrado"
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {product.nombre}. Disponible: {product.stock}, solicitado: {item.quantity}"
                )

            subtotal = product.price * item.quantity

            venta_item = VentaItem(
                venta_id=venta.id,
                product_id=product.id,
                cantidad=item.quantity,
                preciounitario=product.price,
                subtotal=subtotal
            )

            product.stock -= item.quantity
            total += subtotal

            db.add(venta_item)

        venta.total = round(total, 2)

        db.commit()
        db.refresh(venta)

        return venta

    except Exception:
        db.rollback()
        raise
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.venta import Venta, PartidaVenta
from app.models.producto import Producto
from app.models.cliente import Cliente


def listar_ventas(db: Session) -> list[Venta]:
    return db.query(Venta).all()


def listar_ventas_por_fecha(
    db: Session,
    fecha_inicio: datetime | None = None,
    fecha_fin: datetime | None = None,
) -> list[Venta]:
    consulta = db.query(Venta)
    if fecha_inicio:
        consulta = consulta.filter(Venta.created_at >= fecha_inicio)
    if fecha_fin:
        consulta = consulta.filter(Venta.created_at <= fecha_fin)
    return consulta.order_by(Venta.created_at.desc()).all()


def obtener_venta(db: Session, venta_id: int) -> Venta:
    venta = db.query(Venta).filter(
        Venta.id == venta_id
    ).first()

    if not venta:
        raise HTTPException(404, "Venta no encontrada")

    return venta


def crear_venta(db: Session, datos):

    try:
        if datos.cliente_id is not None:
            customer = db.query(Cliente).filter(
                Cliente.id == datos.cliente_id,
                Cliente.activo.is_(True),
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
                Producto.id == item.producto_id,
                Producto.activo.is_(True),
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

        venta.iva = round(total * 0.16, 2)
        venta.total = round(total + venta.iva, 2)

        db.commit()
        db.refresh(venta)

        return venta

    except Exception:
        db.rollback()
        raise


def cancelar_venta(db: Session, venta_id: int) -> Venta:
    try:
        venta = obtener_venta(db, venta_id)
        if venta.estado == "cancelada":
            raise HTTPException(409, "La venta ya está cancelada")

        for item in venta.items:
            producto = db.query(Producto).filter(
                Producto.id == item.producto_id
            ).with_for_update().first()
            if producto:
                producto.stock += item.cantidad

        venta.estado = "cancelada"
        db.commit()
        db.refresh(venta)
        return venta
    except Exception:
        db.rollback()
        raise
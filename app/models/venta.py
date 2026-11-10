from sqlalchemy import Boolean, Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    total = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    iva = Column(Float, nullable=False, default=0)
    estado = Column(String(20), nullable=False, default="activa")

    items = relationship(
        "PartidaVenta",
        back_populates="venta",
        cascade="all, delete-orphan"
    )


class PartidaVenta(Base):
    __tablename__ = "venta_items"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto", backref="partidas_venta")
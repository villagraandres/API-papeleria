from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    total = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    iva = Column(Float, nullable=False, default=0)
    estado = Column(String(20), nullable=False, default="activa")

    items = relationship(
        "PartidaCompra",
        back_populates="compra",
        cascade="all, delete-orphan"
    )


class PartidaCompra(Base):
    __tablename__ = "partidas_compra"

    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("compras.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    compra = relationship("Compra", back_populates="items")
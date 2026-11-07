from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Purchase(Base):
    __tablename__ = "Compras"

    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    total = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship(
        "PurchaseItem",
        back_populates="Compras",
        cascade="all, delete-orphan"
    )


class PurchaseItem(Base):
    __tablename__ = "Compras_Items"

    id = Column(Integer, primary_key=True, index=True)
    compra_id = Column(Integer, ForeignKey("Compras.id"))
    producto_id = Column(Integer, ForeignKey("Productos.id"))
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    Compras = relationship("Compras", back_populates="items")
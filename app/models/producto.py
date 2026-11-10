from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from app.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(255))
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)

    categoria_id = Column(
        Integer,
        ForeignKey("categorias.id"),
        nullable=False
    )
    activo = Column(Boolean, default=True, nullable=False)
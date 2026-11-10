from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    contacto = Column(String(100))
    telefono = Column(String(20))
    correo = Column(String(150))
    activo = Column(Boolean, default=True, nullable=False)
from sqlalchemy import Column, Integer, String
from app.database import Base


class Proveedores(Base):
    __tablename__ = "Proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    contacto = Column(String(100))
    telefono = Column(String(20))
    email = Column(String(150))
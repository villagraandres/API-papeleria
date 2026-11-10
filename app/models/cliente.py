from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    correo = Column(String(150), unique=True, nullable=True)
    telefono = Column(String(20), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
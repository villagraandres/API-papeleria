from sqlalchemy import Column, Integer, String
from app.database import Base


class Clientes(Base):
    __tablename__ = "Clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(20), nullable=False)
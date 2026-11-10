from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255))
    activo = Column(Boolean, default=True, nullable=False)
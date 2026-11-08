from sqlalchemy import Column, Integer, String
from app.database import Base


class Usuario(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    contrasena_encriptada = Column(String(255), nullable=False)
    rol = Column(String(30), default="empleado")
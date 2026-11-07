from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    URLBASEDATOS: str = "sqlite:///./papeleria.db"

    CLAVESECRETA: str = "cambia_esta_clave"
    ALGORITMO: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    class Config:
        env_file = ".env"


configuracion = Configuracion()


motor = create_engine(
    configuracion.URLBASEDATOS,
    connect_args={"check_same_thread": False}
    if configuracion.URLBASEDATOS.startswith("sqlite")
    else {}
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=motor
)


class Base(DeclarativeBase):
    pass


def obtener_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
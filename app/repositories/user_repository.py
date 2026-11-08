from sqlalchemy.orm import Session
from app.models.usuario import Usuario


def obtener_usuario_por_correo(db: Session, correo: str):
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def crear_usuario(db: Session, usuario: Usuario):
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
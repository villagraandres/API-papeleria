from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.usuario import Usuario
from app.repositories.repositorio_usuario import obtener_usuario_por_correo
from app.security import (
    encriptar_contrasena,
    verificar_contrasena,
    crear_token_acceso
)


def registrar_usuario(db: Session, datos):

    usuario_existente = obtener_usuario_por_correo(db, datos.correo)

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    longitud = len(datos.contrasena.encode("utf-8"))
    if longitud < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    if longitud > 72:
        raise HTTPException(
            status_code=400,
            detail="La contraseña no puede superar los 72 bytes"
        )

    usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contrasena_encriptada=encriptar_contrasena(datos.contrasena),
        rol=datos.rol
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def registrar_administrador(db: Session, datos):
    datos_admin = datos.model_copy(update={"rol": "admin"})
    return registrar_usuario(db, datos_admin)


def iniciar_sesion(db: Session, datos):

    usuario = db.query(Usuario).filter(
        Usuario.correo == datos.correo,
        Usuario.activo.is_(True),
    ).first()

    if not usuario or not verificar_contrasena(
        datos.contrasena,
        usuario.contrasena_encriptada
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    token = crear_token_acceso({"sub": usuario.correo})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


def listar_usuarios(db: Session) -> list[Usuario]:
    return db.query(Usuario).all()


def cambiar_estado_usuario(
    db: Session,
    usuario_id: int,
    activo: bool,
    usuario_actual: Usuario,
) -> Usuario:
    usuario_objetivo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario_objetivo:
        raise HTTPException(404, "Usuario no encontrado")
    if not activo and usuario_actual.id == usuario_id:
        raise HTTPException(403, "No es posible desactivar el usuario actual")
    usuario_objetivo.activo = activo
    db.commit()
    db.refresh(usuario_objetivo)
    return usuario_objetivo
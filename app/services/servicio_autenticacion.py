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

    if len(datos.contrasena) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
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

    usuario = obtener_usuario_por_correo(db, datos.correo)

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
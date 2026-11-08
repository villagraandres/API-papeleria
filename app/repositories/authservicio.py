from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.usuario import Usuario
from app.repositories.user_repository import obtener_usuario_por_correo
from app.security import encriptar_contrasena, verificar_contrasena, crear_token_acceso


def register_user(db: Session, data):

    existing_user = obtener_usuario_por_correo(db, data.correo)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    if len(data.contrasena) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )

    user = Usuario(
        nombre=data.nombre,
        correo=data.correo,
        contrasena_encriptada=encriptar_contrasena(data.contrasena),
        rol=data.rol
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(db: Session, data):

    user = obtener_usuario_por_correo(db, data.correo)

    if not user or not verificar_contrasena(
        data.contrasena,
        user.contrasena_encriptada
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    token = crear_token_acceso({"sub": user.correo})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

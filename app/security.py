from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import configuracion, obtener_bd
from app.models.usuario import Usuario


contexto_pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

esquema_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/autenticacion/token"
)

def encriptar_contrasena(contrasena: str):
    if len(contrasena.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar los 72 bytes")
    return contexto_pwd.hash(contrasena)


def verificar_contrasena(contrasena: str, contrasena_encriptada: str):
    return contexto_pwd.verify(contrasena, contrasena_encriptada)


def crear_token_acceso(datos: dict):
    a_codificar = datos.copy()

    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=configuracion.MINUTOS_EXPIRACION_TOKEN
    )

    a_codificar.update({"exp": expiracion})

    return jwt.encode(
        a_codificar,
        configuracion.CLAVESECRETA,
        algorithm=configuracion.ALGORITMO
    )


def obtener_usuario_actual(
    token: str = Depends(esquema_oauth2),
    db: Session = Depends(obtener_bd)
):
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        carga = jwt.decode(
            token,
            configuracion.CLAVESECRETA,
            algorithms=[configuracion.ALGORITMO]
        )

        correo = carga.get("sub")

        if correo is None:
            raise excepcion_credenciales

    except JWTError:
        raise excepcion_credenciales

    usuario = db.query(Usuario).filter(
        Usuario.correo == correo,
        Usuario.activo.is_(True),
    ).first()

    if usuario is None:
        raise excepcion_credenciales

    return usuario


def requerir_admin(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para realizar esta operación"
        )

    return usuario_actual


hash_password = encriptar_contrasena
verify_password = verificar_contrasena
create_access_token = crear_token_acceso
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import obtener_bd
from app.schemas.infoempleado import UsuarioCrear, UsuarioLogin, UsuarioRespuesta
from app.services.servicio_autenticacion import (
    registrar_usuario,
    registrar_administrador,
    iniciar_sesion,
)
from app.security import obtener_usuario_actual, requerir_admin
from app.models.usuario import Usuario


routerautenticacion = APIRouter(prefix="/autenticacion", tags=["Autenticación"])


@routerautenticacion.post("/registro", response_model=UsuarioRespuesta, status_code=201)
def registro(datos: UsuarioCrear, db: Session = Depends(obtener_bd)):

    # El registro público nunca puede crear administradores.
    datos.rol = "empleado"

    return registrar_usuario(db, datos)

@routerautenticacion.post(
    "/registro-admin",
    response_model=UsuarioRespuesta,
    status_code=201,
    dependencies=[Depends(requerir_admin)],
)
def registro_admin(datos: UsuarioCrear, db: Session = Depends(obtener_bd)):
    return registrar_administrador(db, datos)


@routerautenticacion.post("/iniciar-sesion")
def inicio_sesion(datos: UsuarioLogin, db: Session = Depends(obtener_bd)):

    return iniciar_sesion(db, datos)


@routerautenticacion.get("/perfil", response_model=UsuarioRespuesta)
def obtener_perfil(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return usuario_actual
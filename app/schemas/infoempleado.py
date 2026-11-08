from pydantic import BaseModel, EmailStr, ConfigDict


class UsuarioCrear(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    rol: str = "empleado"


class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: str

    model_config = ConfigDict(from_attributes=True)
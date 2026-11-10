from pydantic import BaseModel, EmailStr, ConfigDict


class ClienteCrear(BaseModel):
    nombre: str
    correo: EmailStr | None = None
    telefono: str | None = None


class ClienteRespuesta(BaseModel):
    id: int
    nombre: str
    correo: str | None
    telefono: str | None
    activo: bool

    model_config = ConfigDict(from_attributes=True)
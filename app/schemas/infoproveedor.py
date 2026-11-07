from pydantic import BaseModel, EmailStr, ConfigDict


class ProveedorCrear(BaseModel):
    nombre: str
    contacto: str | None = None
    telefono: str | None = None
    correo: EmailStr | None = None


class ProveedorRespuesta(BaseModel):
    id: int
    nombre: str
    contacto: str | None
    telefono: str | None
    correo: str | None

    model_config = ConfigDict(from_attributes=True)
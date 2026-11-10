from pydantic import BaseModel, ConfigDict


class CategoriaCrear(BaseModel):
    nombre: str
    descripcion: str | None = None


class CategoriaRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool

    model_config = ConfigDict(from_attributes=True)
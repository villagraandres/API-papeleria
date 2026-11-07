from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    nombre: str
    descripcion: str | None = None


class CategoryResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None

    model_config = ConfigDict(from_attributes=True)
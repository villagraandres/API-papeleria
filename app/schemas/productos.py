
from pydantic import BaseModel, Field, ConfigDict


class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str | None = None
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    stock_minimo: int = Field(default=5, ge=0)
    categoria_id: int = Field(gt=0)


class ProductoActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2)
    descripcion: str | None = None
    precio: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    stock_minimo: int | None = Field(default=None, ge=0)
    categoria_id: int | None = Field(default=None, gt=0)


class ProductoRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    precio: float
    stock: int
    stock_minimo: int
    categoria_id: int

    model_config = ConfigDict(from_attributes=True)
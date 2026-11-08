from pydantic import BaseModel, Field, ConfigDict


class PartidaVentaCrear(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class VentaCrear(BaseModel):
    cliente_id: int | None = None
    items: list[PartidaVentaCrear] = Field(min_length=1)


class PartidaVentaRespuesta(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class VentaRespuesta(BaseModel):
    id: int
    cliente_id: int | None
    total: float
    items: list[PartidaVentaRespuesta]

    model_config = ConfigDict(from_attributes=True)
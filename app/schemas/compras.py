from pydantic import BaseModel, Field, ConfigDict


class PartidaCompraCrear(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)
    costo_unitario: float = Field(gt=0)


class CompraCrear(BaseModel):
    proveedor_id: int
    partidas: list[PartidaCompraCrear] = Field(min_length=1)


class PartidaCompraRespuesta(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    costo_unitario: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class CompraRespuesta(BaseModel):
    id: int
    proveedor_id: int
    total: float
    partidas: list[PartidaCompraRespuesta]

    model_config = ConfigDict(from_attributes=True)
from fastapi import FastAPI

from app.database import motor, Base
from app import models

from app.routers import (
    routerautenticacion,
    routerproductos,
    routercategorias,
    routerclientes,
    routerproveedor,
    routercompras,
    routerventa
)


Base.metadata.create_all(bind=motor)


app = FastAPI(
    title="Papelería PIA API",
    description="Sistema de administración de una papelería",
    version="1.0.0"
)



app.include_router(routerautenticacion.routerautenticacion)
app.include_router(routerproductos.routerproducto)
app.include_router(routercategorias.routercategoria)
app.include_router(routerclientes.routercliente)
app.include_router(routerproveedor.routerproveedor)
app.include_router(routerventa.routerventa)
app.include_router(routercompras.routercompra)


@app.get("/")
def home():
    return {
        "message": "Bienvenido al sistema de Papelería PIA",
        "status": "API funcionando"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
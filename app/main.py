from fastapi import FastAPI

from app.database import engine, Base
from app import models

from app.routers import (
    auth,
    routerproductos,
    routercategorias,
    routerclientes,
    routerproveedores,
    routercompras,
    routerventa
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Papelería PIA API",
    description="Sistema de administración de una papelería",
    version="1.0.0"
)



app.include_router(auth.router)
app.include_router(routerproductos.router)
app.include_router(routercategorias.router)
app.include_router(routerclientes.router)
app.include_router(routerproveedores.router)
app.include_router(routerventa.router)
app.include_router(routercompras.router)


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
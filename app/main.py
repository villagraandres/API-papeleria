from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

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

# Interfaz web (HTML/JS estático) en /ui
app.mount(
    "/ui",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="ui",
)


@app.get("/ui", include_in_schema=False)
def redirigir_ui():
    return RedirectResponse("/ui/")


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
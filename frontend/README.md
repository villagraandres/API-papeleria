# Frontend de Papelería PIA

Interfaz estática, sin dependencias adicionales. Consume la API de FastAPI y usa sus rutas y permisos existentes.

## Ejecución local

Desde la raíz del repositorio, inicia la API:

```powershell
poetry run uvicorn app.main:app --reload
```

En otra terminal, sirve esta carpeta:

```powershell
python -m http.server 5500 --directory frontend
```

Abre <http://127.0.0.1:5500>. La dirección de la API se puede cambiar desde la barra superior. La API permite solicitudes CORS desde `localhost:5500` y `127.0.0.1:5500`.

El registro desde la interfaz crea usuarios con rol de empleado. Para administrar productos, categorías, proveedores y compras, inicia sesión con una cuenta que tenga rol de administrador.

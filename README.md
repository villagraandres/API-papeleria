# Papelería PIA

API y aplicación web sencilla para administrar una papelería: usuarios, productos, categorías, clientes, proveedores, compras, ventas e inventario. La API está implementada con FastAPI y usa SQLAlchemy para acceder a la base de datos.

## Requisitos

- Python 3.12 o posterior.
- Poetry 2.x para instalar las dependencias definidas en `pyproject.toml` y `poetry.lock`.

## Instalación

Desde la carpeta raíz del proyecto:

```powershell
poetry install
```

Este comando instala las dependencias de la aplicación y las de desarrollo. Los comandos de las siguientes secciones usan `poetry run`, por lo que no es necesario activar el entorno virtual manualmente.

## Configuración

La configuración se lee de las variables de entorno y del archivo `.env` en la carpeta desde la que se inicia la aplicación. Todos los valores tienen valores predeterminados:

| Variable | Predeterminado | Descripción |
| --- | --- | --- |
| `URLBASEDATOS` | `sqlite:///./papeleria.db` | URL de conexión de SQLAlchemy. Por defecto, crea/usa `papeleria.db` en el directorio de ejecución. |
| `CLAVESECRETA` | `cambia_esta_clave` | Clave usada para firmar los tokens JWT. Debe reemplazarse por una clave aleatoria y privada fuera del desarrollo local. |
| `ALGORITMO` | `HS256` | Algoritmo de firma de los tokens. |
| `MINUTOS_EXPIRACION_TOKEN` | `60` | Duración de los tokens de acceso, en minutos. |

Para desarrollo local, se puede crear un archivo `.env` en la raíz:

```dotenv
URLBASEDATOS=sqlite:///./papeleria.db
CLAVESECRETA=reemplazar-por-una-clave-aleatoria
ALGORITMO=HS256
MINUTOS_EXPIRACION_TOKEN=60
```

No se deben guardar secretos reales en el repositorio. La aplicación crea las tablas al importar `app.main`. SQLite es la base de datos predeterminada; si se configura otra base de datos, se necesita instalar también el controlador correspondiente y usar una URL compatible con SQLAlchemy.

## Ejecutar la aplicación

Desde la raíz del repositorio:

```powershell
poetry run uvicorn app.main:app --reload
```

Por defecto, Uvicorn sirve la aplicación en `http://127.0.0.1:8000`. La opción `--reload` es para desarrollo; no se recomienda en producción.

- Interfaz web: <http://127.0.0.1:8000/ui/>
- Documentación interactiva de la API (Swagger): <http://127.0.0.1:8000/docs>
- Documentación alternativa (ReDoc): <http://127.0.0.1:8000/redoc>
- Estado de la API: <http://127.0.0.1:8000/health>

## Crear el primer administrador

1. Inicia la aplicación al menos una vez para que se creen las tablas.
2. En otra terminal, desde la raíz del proyecto, ejecuta:

   ```powershell
   poetry run python creacionadmin.py
   ```

3. Ingresa el correo, nombre y contraseña solicitados. La contraseña debe tener entre 8 y 72 bytes UTF-8 y el correo no debe estar registrado previamente.

El registro público (`POST /autenticacion/registro`) crea usuarios con rol de empleado. La creación de administradores adicionales requiere autenticarse como administrador.

## Rutas principales

Las rutas y sus parámetros completos están disponibles en `/docs`. Los grupos principales son:

| Prefijo | Funcionalidad |
| --- | --- |
| `/autenticacion` | Registro, inicio de sesión, perfil y administración de usuarios. |
| `/productos` | Consulta, alta, edición y activación/desactivación de productos. |
| `/categorias` | Gestión de categorías. |
| `/clientes` | Gestión de clientes. |
| `/proveedores` | Gestión de proveedores. |
| `/compras` | Registro, consulta y cancelación de compras. |
| `/ventas` | Registro, consulta, cancelación y reporte de ventas. |

El inicio de sesión devuelve un token de acceso. Para las rutas protegidas, envíalo en el encabezado:

```text
Authorization: Bearer <token>
```

La ruta compatible con el formulario OAuth2 de Swagger es `POST /autenticacion/token`; también se puede iniciar sesión enviando JSON a `POST /autenticacion/iniciar-sesion`.

## Dependencias

Las versiones acotadas se especifican en `pyproject.toml` y las versiones resueltas en `poetry.lock`.

**Aplicación**

- FastAPI: API HTTP y validación de solicitudes.
- Uvicorn con extras estándar: servidor ASGI.
- SQLAlchemy: persistencia y acceso a la base de datos.
- pydantic-settings: configuración desde variables de entorno y `.env`.
- python-jose: creación y validación de tokens JWT.
- passlib con bcrypt y bcrypt: hash/verificación de contraseñas.
- email-validator: validación de direcciones de correo.
- python-multipart: recepción de formularios OAuth2.

**Desarrollo y pruebas**

- pytest: ejecución de pruebas.
- httpx: cliente HTTP usado por las pruebas de FastAPI.
- pytest-cov: medición de cobertura.

## Pruebas

Ejecuta la suite desde la raíz:

```powershell
poetry run pytest
```

Para generar un informe de cobertura en la terminal:

```powershell
poetry run pytest --cov=app
```

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, obtener_bd
from app.main import app
from app.models.usuario import Usuario
from app.security import encriptar_contrasena


@pytest.fixture
def cliente() -> Iterator[TestClient]:
    motor_pruebas = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=motor_pruebas)
    sesion_pruebas = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=motor_pruebas,
    )

    with sesion_pruebas() as db:
        db.add(
            Usuario(
                nombre="Admin de pruebas",
                correo="admin.pruebas@example.com",
                contrasena_encriptada=encriptar_contrasena("Admin1234"),
                rol="admin",
                activo=True,
            )
        )
        db.commit()

    def obtener_bd_pruebas() -> Iterator[Session]:
        with sesion_pruebas() as db:
            yield db

    app.dependency_overrides[obtener_bd] = obtener_bd_pruebas
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    motor_pruebas.dispose()


def iniciar_sesion(cliente: TestClient, correo: str, contrasena: str) -> str:
    respuesta = cliente.post(
        "/autenticacion/iniciar-sesion",
        json={"correo": correo, "contrasena": contrasena},
    )
    assert respuesta.status_code == 200
    return respuesta.json()["access_token"]


def encabezado(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_autenticacion_y_gestion_de_usuarios(cliente: TestClient):
    registro = cliente.post(
        "/autenticacion/registro",
        json={
            "nombre": "Empleado de pruebas",
            "correo": "empleado.pruebas@example.com",
            "contrasena": "Empleado123",
            "rol": "admin",
        },
    )
    assert registro.status_code == 201
    assert registro.json()["rol"] == "empleado"
    empleado_id = registro.json()["id"]

    admin_token = iniciar_sesion(
        cliente,
        "admin.pruebas@example.com",
        "Admin1234",
    )
    admin_headers = encabezado(admin_token)

    perfil = cliente.get("/autenticacion/perfil", headers=admin_headers)
    assert perfil.status_code == 200
    assert perfil.json()["rol"] == "admin"

    registro_admin = cliente.post(
        "/autenticacion/registro-admin",
        headers=admin_headers,
        json={
            "nombre": "Segundo administrador",
            "correo": "segundo.admin@example.com",
            "contrasena": "Admin5678",
        },
    )
    assert registro_admin.status_code == 201
    assert registro_admin.json()["rol"] == "admin"

    usuarios = cliente.get("/autenticacion/usuarios", headers=admin_headers)
    assert usuarios.status_code == 200
    assert len(usuarios.json()) == 3

    desactivar = cliente.patch(
        f"/autenticacion/usuarios/{empleado_id}/desactivar",
        headers=admin_headers,
    )
    assert desactivar.status_code == 200
    assert desactivar.json()["activo"] is False

    login_inactivo = cliente.post(
        "/autenticacion/iniciar-sesion",
        json={
            "correo": "empleado.pruebas@example.com",
            "contrasena": "Empleado123",
        },
    )
    assert login_inactivo.status_code == 401

    activar = cliente.patch(
        f"/autenticacion/usuarios/{empleado_id}/activar",
        headers=admin_headers,
    )
    assert activar.status_code == 200
    assert activar.json()["activo"] is True

    admin_id = perfil.json()["id"]
    no_se_desactiva_a_si_mismo = cliente.patch(
        f"/autenticacion/usuarios/{admin_id}/desactivar",
        headers=admin_headers,
    )
    assert no_se_desactiva_a_si_mismo.status_code == 403


def test_catalogos_producto_y_desactivacion(cliente: TestClient):
    admin_token = iniciar_sesion(
        cliente,
        "admin.pruebas@example.com",
        "Admin1234",
    )
    admin_headers = encabezado(admin_token)

    categoria = cliente.post(
        "/categorias/",
        headers=admin_headers,
        json={"nombre": "Papelería de pruebas", "descripcion": "Pruebas"},
    )
    assert categoria.status_code == 201
    categoria_id = categoria.json()["id"]

    cliente_respuesta = cliente.post(
        "/clientes/",
        headers=admin_headers,
        json={
            "nombre": "Cliente de pruebas",
            "correo": "cliente.pruebas@example.com",
            "telefono": "5550001",
        },
    )
    assert cliente_respuesta.status_code == 201
    cliente_id = cliente_respuesta.json()["id"]

    proveedor = cliente.post(
        "/proveedores/",
        headers=admin_headers,
        json={
            "nombre": "Proveedor de pruebas",
            "contacto": "Contacto",
            "correo": "proveedor.pruebas@example.com",
        },
    )
    assert proveedor.status_code == 201
    proveedor_id = proveedor.json()["id"]

    producto = cliente.post(
        "/productos/",
        headers=admin_headers,
        json={
            "nombre": "Producto de pruebas",
            "descripcion": "Producto para integración",
            "precio": 10,
            "stock": 10,
            "stock_minimo": 2,
            "categoria_id": categoria_id,
        },
    )
    assert producto.status_code == 201
    producto_id = producto.json()["id"]

    actualizado = cliente.put(
        f"/productos/{producto_id}",
        headers=admin_headers,
        json={"nombre": "Producto actualizado", "precio": 12},
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["nombre"] == "Producto actualizado"
    assert actualizado.json()["precio"] == 12

    desactivaciones = [
        (f"/categorias/{categoria_id}/desactivar", "/categorias/"),
        (f"/clientes/{cliente_id}/desactivar", "/clientes/"),
        (f"/proveedores/{proveedor_id}/desactivar", "/proveedores/"),
        (f"/productos/{producto_id}/desactivar", "/productos/"),
    ]
    for ruta, listado in desactivaciones:
        assert cliente.patch(ruta, headers=admin_headers).status_code == 204
        ids = {registro["id"] for registro in cliente.get(listado).json()}
        assert (
            categoria_id
            if listado == "/categorias/"
            else cliente_id
            if listado == "/clientes/"
            else proveedor_id
            if listado == "/proveedores/"
            else producto_id
        ) not in ids

    reactivaciones = [
        f"/categorias/{categoria_id}/activar",
        f"/clientes/{cliente_id}/activar",
        f"/proveedores/{proveedor_id}/activar",
        f"/productos/{producto_id}/activar",
    ]
    for ruta in reactivaciones:
        assert cliente.patch(ruta, headers=admin_headers).status_code == 204

    producto_invalido = cliente.post(
        "/productos/",
        headers=admin_headers,
        json={
            "nombre": "Sin categoría",
            "precio": 5,
            "stock": 1,
            "categoria_id": 99999,
        },
    )
    assert producto_invalido.status_code == 404

def test_compras_ventas_inventario_cancelacion_y_reportes(cliente: TestClient):
    admin_token = iniciar_sesion(
        cliente,
        "admin.pruebas@example.com",
        "Admin1234",
    )
    admin_headers = encabezado(admin_token)

    categoria = cliente.post(
        "/categorias/",
        headers=admin_headers,
        json={"nombre": "Categoría transaccional"},
    ).json()
    cliente_id = cliente.post(
        "/clientes/",
        headers=admin_headers,
        json={"nombre": "Cliente transaccional"},
    ).json()["id"]
    proveedor_id = cliente.post(
        "/proveedores/",
        headers=admin_headers,
        json={"nombre": "Proveedor transaccional"},
    ).json()["id"]
    producto_id = cliente.post(
        "/productos/",
        headers=admin_headers,
        json={
            "nombre": "Producto transaccional",
            "precio": 10,
            "stock": 10,
            "categoria_id": categoria["id"],
        },
    ).json()["id"]

    compra = cliente.post(
        "/compras/",
        headers=admin_headers,
        json={
            "proveedor_id": proveedor_id,
            "items": [
                {
                    "producto_id": producto_id,
                    "cantidad": 5,
                    "costo_unitario": 6,
                }
            ],
        },
    )
    assert compra.status_code == 201
    assert compra.json()["iva"] == 4.8
    assert compra.json()["total"] == 34.8
    compra_id = compra.json()["id"]

    producto = cliente.get(f"/productos/{producto_id}").json()
    assert producto["stock"] == 15

    venta = cliente.post(
        "/ventas/",
        headers=admin_headers,
        json={
            "cliente_id": cliente_id,
            "items": [{"producto_id": producto_id, "cantidad": 2}],
        },
    )
    assert venta.status_code == 201
    assert venta.json()["iva"] == 3.2
    assert venta.json()["total"] == 23.2
    venta_id = venta.json()["id"]
    assert cliente.get(f"/productos/{producto_id}").json()["stock"] == 13

    ventas = cliente.get("/ventas/", headers=admin_headers)
    assert ventas.status_code == 200
    assert any(item["id"] == venta_id for item in ventas.json())

    compra_obtenida = cliente.get(
        f"/compras/{compra_id}",
        headers=admin_headers,
    )
    assert compra_obtenida.status_code == 200

    cancelar_venta = cliente.patch(
        f"/ventas/{venta_id}/cancelar",
        headers=admin_headers,
    )
    assert cancelar_venta.status_code == 200
    assert cancelar_venta.json()["estado"] == "cancelada"
    assert cliente.get(f"/productos/{producto_id}").json()["stock"] == 15

    cancelar_compra = cliente.patch(
        f"/compras/{compra_id}/cancelar",
        headers=admin_headers,
    )
    assert cancelar_compra.status_code == 200
    assert cancelar_compra.json()["estado"] == "cancelada"
    assert cliente.get(f"/productos/{producto_id}").json()["stock"] == 10

    assert cliente.patch(
        f"/ventas/{venta_id}/cancelar",
        headers=admin_headers,
    ).status_code == 409
    assert cliente.patch(
        f"/compras/{compra_id}/cancelar",
        headers=admin_headers,
    ).status_code == 409


def test_validaciones_y_permisos(cliente: TestClient):
    registro = cliente.post(
        "/autenticacion/registro",
        json={
            "nombre": "Empleado sin permisos",
            "correo": "sin.permisos@example.com",
            "contrasena": "Empleado123",
        },
    )
    assert registro.status_code == 201
    token = iniciar_sesion(
        cliente,
        "sin.permisos@example.com",
        "Empleado123",
    )
    headers = encabezado(token)

    sin_permisos = cliente.post(
        "/categorias/",
        headers=headers,
        json={"nombre": "No autorizada"},
    )
    assert sin_permisos.status_code == 403

    sin_autenticacion = cliente.get("/ventas/")
    assert sin_autenticacion.status_code == 401

    contraseña_larga = cliente.post(
        "/autenticacion/registro",
        json={
            "nombre": "Contraseña inválida",
            "correo": "larga@example.com",
            "contrasena": "x" * 73,
        },
    )
    assert contraseña_larga.status_code == 400

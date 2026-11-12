from fastapi.testclient import TestClient
from app.main import app

cliente = TestClient(app)


def test_sale_requires_authentication():

    response = cliente.post(
        "/ventas/",
        json={
            "customer_id": None,
            "items": [
                {
                    "producto_id": 1,
                    "cantidad": 2
                }
            ]
        }
    )

    assert response.status_code == 401


def test_sale_requires_authentication_before_items_validation():

    response = cliente.post(
        "/ventas/",
        json={
            "cliente_id": None,
            "items": []
        }
    )

    # Las rutas protegidas autentican antes de validar las reglas del negocio.
    assert response.status_code == 401

from fastapi.testclient import TestClient
from app.main import app

cliente = TestClient(app)


def test_home():
    response = cliente.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "API funcionando"


def test_list_products():
    response = cliente.get("/productos/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_product_requires_authentication():
    response = cliente.post(
        "/productos/",
        json={
            "Nombre": "Cuaderno profesional",
            "Descripcion": "Cuaderno de 100 hojas",
            "Precio": 45.50,
            "stock": 20,
            "min_stock": 5,
            "categoria_id": 1
        }
    )

    assert response.status_code == 401

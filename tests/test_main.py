import pytest
from core.config import ADMIN_SECRET
from fastapi.testclient import TestClient
from core.main import app


client = TestClient(app)
client.headers.update({"x-api-key": ADMIN_SECRET})


def test_read_items():
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_order():
    order_data = {
        "order_items": [{"id": 1}],
        "user_id": 123,
        "total_price": 100.0
    }
    response = client.post("/order/", json=order_data)
    assert response.status_code == 201
    assert "order_id" in response.json()

from web.core.config import ADMIN_SECRET
from fastapi.testclient import TestClient
from web.core.main import app


client = TestClient(app)
client.headers.update({"x-api-key": ADMIN_SECRET})


def check_status_code(response, expected_status_code):
    assert response.status_code == expected_status_code, (
        f"Incorrect status code: {response.status_code}, expected {expected_status_code}"
    )


def test_read_items():
    response = client.get("/items/")
    check_status_code(response, 200)
    assert isinstance(response.json(), list)


def test_create_order():
    order_data = {"order_items": [{"id": 1}], "user_id": 123, "total_price": 100.0}
    response = client.post("/order/", json=order_data)
    check_status_code(response, 201)
    assert "order_id" in response.json()
    assert isinstance(response.json()["order_id"], int)


def test_read_orders():
    response = client.get("/orders/")
    check_status_code(response, 200)
    assert isinstance(response.json(), list)


def test_forbidden_access_to_api():
    client.headers["x-api-key"] = "wrong"
    response = client.get("/items/")
    check_status_code(response, 403)
    client.headers.clear()
    response = client.get("/orders/")
    check_status_code(response, 403)

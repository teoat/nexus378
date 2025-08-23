from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_anonymize_user():
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "address": "123 Main St",
    }

    response = client.post(
        "/anonymize_user", json={"user_id": "user123", "data": user_data}
    )
    assert response.status_code == 200
    anonymized_data = response.json()["anonymized_data"]

    assert anonymized_data["name"] == "[REDACTED]"
    assert anonymized_data["email"] == "[REDACTED]"
    assert anonymized_data["address"] == "[REDACTED]"

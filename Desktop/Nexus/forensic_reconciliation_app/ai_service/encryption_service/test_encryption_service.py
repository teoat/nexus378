from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_encrypt_decrypt():
    original_data = "This is a secret message."

    # Test encryption
    response = client.post("/encrypt", json={"data": original_data})
    assert response.status_code == 200
    encrypted_data = response.json()["encrypted_data"]
    assert encrypted_data != original_data

    # Test decryption
    response = client.post("/decrypt", json={"encrypted_data": encrypted_data})
    assert response.status_code == 200
    decrypted_data = response.json()["data"]
    assert decrypted_data == original_data

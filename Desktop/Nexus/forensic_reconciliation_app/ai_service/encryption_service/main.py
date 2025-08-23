from fastapi import FastAPI
from pydantic import BaseModel

from .encryption import ENCRYPTION_KEY, decrypt, encrypt

app = FastAPI()


class EncryptionRequest(BaseModel):
    data: str


class EncryptionResponse(BaseModel):
    encrypted_data: str


class DecryptionRequest(BaseModel):
    encrypted_data: str


class DecryptionResponse(BaseModel):
    data: str


@app.post("/encrypt", response_model=EncryptionResponse)
async def encrypt_data(request: EncryptionRequest):
    encrypted_data = encrypt(request.data, ENCRYPTION_KEY)
    return EncryptionResponse(encrypted_data=encrypted_data)


@app.post("/decrypt", response_model=DecryptionResponse)
async def decrypt_data(request: DecryptionRequest):
    decrypted_data = decrypt(request.encrypted_data, ENCRYPTION_KEY)
    return DecryptionResponse(data=decrypted_data)

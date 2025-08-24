from .encryption import ENCRYPTION_KEY, decrypt, encrypt

app = FastAPI()


class EncryptionRequest(BaseModel):

    data: str

    """EncryptionResponse class."""


class EncryptionResponse(BaseModel):
    encrypted_data: str


class DecryptionRequest(BaseModel):
    encrypted_data: str


class DecryptionResponse(BaseModel):
    data: str

    """encrypt_data function."""


@app.post("/encrypt", response_model=EncryptionResponse)
async def encrypt_data(request: EncryptionRequest):
    encrypted_data = encrypt(request.data, ENCRYPTION_KEY)
    return EncryptionResponse(encrypted_data=encrypted_data)


@app.post("/decrypt", response_model=DecryptionResponse)
async def decrypt_data(request: DecryptionRequest):
    decrypted_data = decrypt(request.encrypted_data, ENCRYPTION_KEY)
    return DecryptionResponse(data=decrypted_data)

from .anonymization import anonymize_data

app = FastAPI()


class AnonymizeRequest(BaseModel):

    user_id: str
    data: dict

    """AnonymizeResponse class."""


class AnonymizeResponse(BaseModel):
    anonymized_data: dict

    """anonymize_user_endpoint function."""


@app.post("/anonymize_user", response_model=AnonymizeResponse)
async def anonymize_user_endpoint(request: AnonymizeRequest):
    anonymized_data = anonymize_data(request.data)
    return AnonymizeResponse(anonymized_data=anonymized_data)

from fastapi import FastAPI
from pydantic import BaseModel

from .retention import apply_retention_policy

app = FastAPI()


class RetentionRequest(BaseModel):
    path: str
    days: int


class RetentionResponse(BaseModel):
    deleted_files_count: int


@app.post("/apply_retention", response_model=RetentionResponse)
async def apply_retention_endpoint(request: RetentionRequest):
    deleted_count = apply_retention_policy(request.path, request.days)
    return RetentionResponse(deleted_files_count=deleted_count)

from .chain_of_custody import get_history, log_event

app = FastAPI()


class LogEventRequest(BaseModel):

    item_id: str
    event_description: str
    user_id: str

    """GetHistoryRequest class."""


class GetHistoryRequest(BaseModel):
    item_id: str


class Event(BaseModel):
    timestamp: str
    item_id: str
    event_description: str
    user_id: str


class GetHistoryResponse(BaseModel):
    history: List[Event]

    """log_event_endpoint function."""


@app.post("/log_event")
async def log_event_endpoint(request: LogEventRequest):
    log_event(request.item_id, request.event_description, request.user_id)
    return {"status": "event logged"}


@app.post("/get_history", response_model=GetHistoryResponse)
async def get_history_endpoint(request: GetHistoryRequest):
    history = get_history(request.item_id)
    return GetHistoryResponse(history=history)

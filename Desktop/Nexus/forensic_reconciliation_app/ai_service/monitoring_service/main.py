from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# This is a placeholder for the global Taskmaster instance.
# In a real application, this would be handled by a proper service discovery mechanism.
taskmaster_instance = None

try:
    from ..taskmaster.core.taskmaster import taskmaster as global_taskmaster
    taskmaster_instance = global_taskmaster
except ImportError:
    pass

app = FastAPI()

class QueueStatusResponse(BaseModel):
    queue_status: Dict[str, Any]

@app.get("/queues", response_model=QueueStatusResponse)
async def get_queues_status():
    if not taskmaster_instance:
        raise HTTPException(status_code=503, detail="Taskmaster service is not available.")

    queue_status = await taskmaster_instance.get_queue_status()
    return QueueStatusResponse(queue_status=queue_status)

"""
Queue Data Model
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import timedelta

class QueueType(Enum):
    HIGH_PRIORITY = "high_priority"
    NORMAL = "normal"
    BATCH = "batch"
    MAINTENANCE = "maintenance"

class QueueStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"

class QueuePolicy(Enum):
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"

@dataclass
class Queue:
    name: str
    queue_type: QueueType
    status: QueueStatus = QueueStatus.ACTIVE
    policy: QueuePolicy = QueuePolicy.FIFO
    max_size: int = 1000
    workers: int = 1
    job_ids: List[str] = field(default_factory=list)
    timeout: timedelta = timedelta(hours=1)
    retry_policy: Optional[str] = None

    def __len__(self):
        return len(self.job_ids)

    async def start(self):
        pass

    async def stop(self):
        pass

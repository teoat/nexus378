"""
Task Data Model
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class TaskDependency:
    from_task: str
    to_task: str

@dataclass
class Task:
    task_id: str
    job_id: str
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[TaskDependency] = field(default_factory=list)
    result: Optional[TaskResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

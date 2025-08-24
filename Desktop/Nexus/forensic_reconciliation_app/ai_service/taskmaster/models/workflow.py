"""
Workflow Data Model
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    step_id: str
    job_id: str
    name: str
    description: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    dependencies: List[str] = field(default_factory=list)

@dataclass
class WorkflowDependency:
    from_step: str
    to_step: str

@dataclass
class Workflow:
    workflow_id: str
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep] = field(default_factory=list)
    dependencies: List[WorkflowDependency] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)

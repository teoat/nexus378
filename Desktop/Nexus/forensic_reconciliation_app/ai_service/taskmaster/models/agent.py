"""
Agent Data Model
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"

class AgentType(Enum):
    GENERAL = "general"
    SPECIALIZED = "specialized"

class AgentCapability(Enum):
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    INFRASTRUCTURE = "infrastructure"
    RECONCILIATION = "reconciliation"
    FRAUD_DETECTION = "fraud_detection"

@dataclass
class Agent:
    agent_id: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[AgentCapability] = field(default_factory=list)
    current_job_id: Optional[str] = None
    last_heartbeat: Optional[str] = None

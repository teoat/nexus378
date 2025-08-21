"""
Job Data Model

This module contains the Job class and related enums for representing
jobs in the Taskmaster system.
"""

import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    MAINTENANCE = "maintenance"


class JobType(Enum):
    """Job type enumeration."""
    # Reconciliation jobs
    BANK_STATEMENT_PROCESSING = "bank_statement_processing"
    RECEIPT_MATCHING = "receipt_matching"
    TRANSACTION_ANALYSIS = "transaction_analysis"
    OUTLIER_DETECTION = "outlier_detection"

    # Fraud detection jobs
    ENTITY_NETWORK_ANALYSIS = "entity_network_analysis"
    PATTERN_DETECTION = "pattern_detection"
    RISK_ASSESSMENT = "risk_assessment"
    ANOMALY_DETECTION = "anomaly_detection"
    
    # Evidence processing jobs
    FILE_UPLOAD = "file_upload"
    HASH_VERIFICATION = "hash_verification"
    EXIF_EXTRACTION = "exif_extraction"
    NLP_PROCESSING = "nlp_processing"
    
    # Litigation support jobs
    CASE_CREATION = "case_creation"
    TIMELINE_BUILDING = "timeline_building"
    REPORT_GENERATION = "report_generation"
    EVIDENCE_LINKING = "evidence_linking"
    
    # Compliance monitoring jobs
    SOX_COMPLIANCE = "sox_compliance"
    PCI_VALIDATION = "pci_validation"
    AML_SCREENING = "aml_screening"
    GDPR_AUDIT = "gdpr_audit"


@dataclass
class JobResult:
    """Result of a completed job."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate job result after initialization."""
        if self.success and self.error_message:
            raise ValueError("Successful jobs cannot have error messages")

        if not self.success and not self.error_message:
            raise ValueError("Failed jobs must have error messages")


@dataclass
class Job:
    """
    Job representation in the Taskmaster system.
    
    A job represents a unit of work that needs to be executed by one or more
    AI agents. Jobs can be simple (single task) or complex (workflow-based).
    """
    
    # Core identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    description: Optional[str] = None
    
    # Job classification
    job_type: JobType = JobType.TRANSACTION_ANALYSIS
    priority: JobPriority = JobPriority.NORMAL
    category: Optional[str] = None
    
    # Data and parameters
    data: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution control
    status: JobStatus = JobStatus.PENDING
    max_retries: int = 3
    retry_count: int = 0
    timeout: Optional[timedelta] = None
    
    # Dependencies and relationships
    dependencies: List[str] = field(default_factory=list)  # List of job IDs
    parent_job_id: Optional[str] = None
    child_job_ids: List[str] = field(default_factory=list)
    workflow_id: Optional[str] = None
    
    # Scheduling and execution
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Assignment and routing
    assigned_agent_id: Optional[str] = None
    assigned_queue: Optional[str] = None
    routing_key: Optional[str] = None
    
    # Results and outcomes
    result: Optional[JobResult] = None
    progress: float = 0.0  # 0.0 to 1.0
    estimated_completion: Optional[datetime] = None
    
    # Audit and tracking
    created_by: Optional[str] = None
    assigned_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and set defaults after initialization."""
        # Set default name if not provided
        if not self.name:
            self.name = f"{self.job_type.value}_{self.id[:8]}"
        
        # Set default timeout based on priority
        if not self.timeout:
            self.timeout = self._get_default_timeout()
        
        # Set default deadline if not provided
        if not self.deadline:
            self.deadline = self.created_at + self.timeout

    def _get_default_timeout(self) -> timedelta:
        """Get default timeout based on job priority."""
        timeout_map = {
            JobPriority.CRITICAL: timedelta(minutes=5),
            JobPriority.HIGH: timedelta(minutes=30),
            JobPriority.NORMAL: timedelta(hours=4),
            JobPriority.LOW: timedelta(hours=24),
            JobPriority.MAINTENANCE: timedelta(hours=1)
        }
        return timeout_map.get(self.priority, timedelta(hours=4))
    
    def can_start(self) -> bool:
        """Check if the job can start execution."""
        return (
            self.status == JobStatus.QUEUED and
            not self._has_pending_dependencies() and
            not self._is_timed_out()
        )
    
    def can_retry(self) -> bool:
        """Check if the job can be retried."""
        return (
            self.status in [JobStatus.FAILED, JobStatus.TIMEOUT] and
            self.retry_count < self.max_retries
        )
    
    def is_completed(self) -> bool:
        """Check if the job is completed (successfully or with failure)."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def is_active(self) -> bool:
        """Check if the job is currently active."""
        return self.status in [JobStatus.RUNNING, JobStatus.RETRYING]
    
    def is_pending(self) -> bool:
        """Check if the job is waiting to be processed."""
        return self.status in [JobStatus.PENDING, JobStatus.QUEUED]

    def _has_pending_dependencies(self) -> bool:
        """Check if the job has pending dependencies."""
        # This would typically check with the job scheduler
        # For now, return False as a placeholder
        return False

    def _is_timed_out(self) -> bool:
        """Check if the job has timed out."""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline

    def start_execution(self, agent_id: str) -> None:
        """Mark the job as started and assign an agent."""
        if not self.can_start():
            raise RuntimeError(f"Job {self.id} cannot start execution")
        
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.assigned_agent_id = agent_id
        self.progress = 0.0

    def complete_execution(self, result: JobResult) -> None:
        """Mark the job as completed with results."""
        if self.status != JobStatus.RUNNING:
            raise RuntimeError(f"Job {self.id} is not running")
        
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result = result
        self.progress = 1.0
        
        # Calculate execution time
        if self.started_at:
            execution_time = (self.completed_at - self.started_at).total_seconds()
            result.execution_time = execution_time

    def fail_execution(self, error_message: str, error_code: Optional[str] = None) -> None:
        """Mark the job as failed."""
        if self.status != JobStatus.RUNNING:
            raise RuntimeError(f"Job {self.id} is not running")
        
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.result = JobResult(
            success=False,
            error_message=error_message,
            error_code=error_code
        )

    def retry_execution(self) -> None:
        """Mark the job for retry."""
        if not self.can_retry():
            raise RuntimeError(f"Job {self.id} cannot be retried")
        
        self.retry_count += 1
        self.status = JobStatus.RETRYING
        self.started_at = None
        self.completed_at = None
        self.assigned_agent_id = None
        self.progress = 0.0

    def cancel_execution(self) -> None:
        """Cancel the job execution."""
        if self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            raise RuntimeError(f"Job {self.id} cannot be cancelled")

        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def update_progress(self, progress: float) -> None:
        """Update the job progress."""
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        self.progress = progress
        
        # Update estimated completion
        if self.started_at and progress > 0.0:
            elapsed_time = (datetime.utcnow() - self.started_at).total_seconds()
            estimated_total_time = elapsed_time / progress
            estimated_remaining = estimated_total_time - elapsed_time
            self.estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_remaining)

    def add_dependency(self, job_id: str) -> None:
        """Add a dependency to this job."""
        if job_id not in self.dependencies:
            self.dependencies.append(job_id)

    def remove_dependency(self, job_id: str) -> None:
        """Remove a dependency from this job."""
        if job_id in self.dependencies:
            self.dependencies.remove(job_id)

    def add_child_job(self, job_id: str) -> None:
        """Add a child job to this job."""
        if job_id not in self.child_job_ids:
            self.child_job_ids.append(job_id)

    def remove_child_job(self, job_id: str) -> None:
        """Remove a child job from this job."""
        if job_id in self.child_job_ids:
            self.child_job_ids.remove(job_id)

    def add_note(self, note: str) -> None:
        """Add a note to the job."""
        self.notes.append(f"{datetime.utcnow().isoformat()}: {note}")

    def add_tag(self, tag: str) -> None:
        """Add a tag to the job."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the job."""
        if tag in self.tags:
            self.tags.remove(tag)

    def get_age(self) -> timedelta:
        """Get the age of the job."""
        return datetime.utcnow() - self.created_at

    def get_execution_time(self) -> Optional[timedelta]:
        """Get the execution time of the job."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def get_wait_time(self) -> Optional[timedelta]:
        """Get the wait time of the job."""
        if self.started_at:
            return self.started_at - self.created_at
        return None

    def get_remaining_time(self) -> Optional[timedelta]:
        """Get the remaining time before timeout."""
        if not self.deadline:
            return None
        
        remaining = self.deadline - datetime.utcnow()
        return remaining if remaining > timedelta(0) else timedelta(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the job to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "job_type": self.job_type.value,
            "priority": self.priority.value,
            "category": self.category,
            "status": self.status.value,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "timeout": self.timeout.total_seconds() if self.timeout else None,
            "dependencies": self.dependencies,
            "parent_job_id": self.parent_job_id,
            "child_job_ids": self.child_job_ids,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "assigned_agent_id": self.assigned_agent_id,
            "assigned_queue": self.assigned_queue,
            "routing_key": self.routing_key,
            "progress": self.progress,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "created_by": self.created_by,
            "assigned_by": self.assigned_by,
            "tags": self.tags,
            "notes": self.notes,
            "result": self.result.to_dict() if self.result else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create a job from a dictionary representation."""
        # Convert string values back to enums
        if "job_type" in data:
            data["job_type"] = JobType(data["job_type"])
        
        if "priority" in data:
            data["priority"] = JobPriority(data["priority"])

        if "status" in data:
            data["status"] = JobStatus(data["status"])

        # Convert timeout back to timedelta
        if "timeout" in data and data["timeout"]:
            data["timeout"] = timedelta(seconds=data["timeout"])

        # Convert datetime strings back to datetime objects
        datetime_fields = ["created_at", "scheduled_at", "started_at", "completed_at", "deadline", "estimated_completion"]
        for field in datetime_fields:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert result back to JobResult
        if "result" in data and data["result"]:
            data["result"] = JobResult(**data["result"])

        return cls(**data)

    def __repr__(self) -> str:
        """String representation of the job."""
        return f"Job(id={self.id}, type={self.job_type.value}, status={self.status.value}, priority={self.priority.value})"

    def __eq__(self, other: object) -> bool:
        """Check if two jobs are equal."""
        if not isinstance(other, Job):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash the job based on its ID."""
        return hash(self.id)

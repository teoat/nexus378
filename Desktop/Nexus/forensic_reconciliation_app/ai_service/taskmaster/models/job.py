"""
Job Model - Comprehensive Job Management System

This module defines the Job model and related components for the Taskmaster system,
including all job types, priorities, and statuses needed for forensic investigations.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class JobType(Enum):
    """Job types for the forensic platform."""
    
    # Evidence Processing Jobs
    EVIDENCE_COLLECTION = "evidence_collection"
    EVIDENCE_ANALYSIS = "evidence_analysis"
    EVIDENCE_INDEXING = "evidence_indexing"
    EVIDENCE_VERIFICATION = "evidence_verification"
    EVIDENCE_ENCRYPTION = "evidence_encryption"
    EVIDENCE_DECRYPTION = "evidence_decryption"
    
    # File Processing Jobs
    FILE_UPLOAD = "file_upload"
    FILE_PROCESSING = "file_processing"
    FILE_ANALYSIS = "file_analysis"
    FILE_CONVERSION = "file_conversion"
    FILE_EXTRACTION = "file_extraction"
    FILE_COMPRESSION = "file_compression"
    
    # Document Analysis Jobs
    DOCUMENT_OCR = "document_ocr"
    DOCUMENT_PARSING = "document_parsing"
    DOCUMENT_ANALYSIS = "document_analysis"
    DOCUMENT_CLASSIFICATION = "document_classification"
    DOCUMENT_SUMMARIZATION = "document_summarization"
    DOCUMENT_TRANSLATION = "document_translation"
    
    # Image Analysis Jobs
    IMAGE_ANALYSIS = "image_analysis"
    IMAGE_ENHANCEMENT = "image_enhancement"
    IMAGE_FORENSICS = "image_forensics"
    IMAGE_METADATA_EXTRACTION = "image_metadata_extraction"
    IMAGE_STEGANOGRAPHY_DETECTION = "image_steganography_detection"
    
    # Video Analysis Jobs
    VIDEO_ANALYSIS = "video_analysis"
    VIDEO_ENHANCEMENT = "video_enhancement"
    VIDEO_FORENSICS = "video_forensics"
    VIDEO_FRAME_EXTRACTION = "video_frame_extraction"
    VIDEO_METADATA_EXTRACTION = "video_metadata_extraction"
    
    # Audio Analysis Jobs
    AUDIO_ANALYSIS = "audio_analysis"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    AUDIO_FORENSICS = "audio_forensics"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_SPEAKER_IDENTIFICATION = "audio_speaker_identification"
    
    # Network Analysis Jobs
    NETWORK_TRAFFIC_ANALYSIS = "network_traffic_analysis"
    NETWORK_FORENSICS = "network_forensics"
    NETWORK_PACKET_ANALYSIS = "network_packet_analysis"
    NETWORK_INTRUSION_DETECTION = "network_intrusion_detection"
    
    # Memory Analysis Jobs
    MEMORY_DUMP_ANALYSIS = "memory_dump_analysis"
    MEMORY_FORENSICS = "memory_forensics"
    MEMORY_ARTIFACT_EXTRACTION = "memory_artifact_extraction"
    
    # Database Analysis Jobs
    DATABASE_FORENSICS = "database_forensics"
    DATABASE_QUERY_ANALYSIS = "database_query_analysis"
    DATABASE_RECOVERY = "database_recovery"
    
    # Mobile Device Analysis Jobs
    MOBILE_FORENSICS = "mobile_forensics"
    MOBILE_APP_ANALYSIS = "mobile_app_analysis"
    MOBILE_DATA_EXTRACTION = "mobile_data_extraction"
    
    # AI/ML Analysis Jobs
    AI_ANALYSIS = "ai_analysis"
    ML_MODEL_TRAINING = "ml_model_training"
    ML_MODEL_INFERENCE = "ml_model_inference"
    PATTERN_DETECTION = "pattern_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    
    # Fraud Detection Jobs
    FRAUD_DETECTION = "fraud_detection"
    FRAUD_ANALYSIS = "fraud_analysis"
    FRAUD_PATTERN_ANALYSIS = "fraud_pattern_analysis"
    FRAUD_SCORING = "fraud_scoring"
    
    # Risk Assessment Jobs
    RISK_ASSESSMENT = "risk_assessment"
    RISK_ANALYSIS = "risk_analysis"
    RISK_SCORING = "risk_scoring"
    RISK_MODELING = "risk_modeling"
    
    # Compliance Jobs
    COMPLIANCE_CHECK = "compliance_check"
    COMPLIANCE_AUDIT = "compliance_audit"
    COMPLIANCE_REPORTING = "compliance_reporting"
    REGULATORY_ANALYSIS = "regulatory_analysis"
    
    # Investigation Jobs
    INVESTIGATION_ANALYSIS = "investigation_analysis"
    CASE_MANAGEMENT = "case_management"
    TIMELINE_CONSTRUCTION = "timeline_construction"
    EVIDENCE_LINKING = "evidence_linking"
    
    # Reporting Jobs
    REPORT_GENERATION = "report_generation"
    REPORT_ANALYSIS = "report_analysis"
    REPORT_FORMATTING = "report_formatting"
    REPORT_DISTRIBUTION = "report_distribution"
    
    # System Jobs
    SYSTEM_MAINTENANCE = "system_maintenance"
    BACKUP_OPERATION = "backup_operation"
    CLEANUP_OPERATION = "cleanup_operation"
    MONITORING_OPERATION = "monitoring_operation"
    
    # Custom Jobs
    CUSTOM_JOB = "custom_job"
    BATCH_PROCESSING = "batch_processing"
    DATA_MIGRATION = "data_migration"
    INTEGRATION_TASK = "integration_task"


class JobPriority(Enum):
    """Job priority levels."""
    CRITICAL = "critical"      # Immediate attention required
    HIGH = "high"              # High priority, process soon
    MEDIUM = "medium"          # Normal priority
    LOW = "low"                # Low priority, process when possible
    BATCH = "batch"            # Batch processing priority
    MAINTENANCE = "maintenance"  # System maintenance priority


class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"        # Job is waiting to be processed
    QUEUED = "queued"          # Job is in processing queue
    ASSIGNED = "assigned"      # Job has been assigned to an agent
    RUNNING = "running"        # Job is currently being processed
    PAUSED = "paused"         # Job processing has been paused
    RESUMED = "resumed"        # Job processing has been resumed
    COMPLETED = "completed"    # Job has been completed successfully
    FAILED = "failed"          # Job processing failed
    CANCELLED = "cancelled"    # Job has been cancelled
    TIMEOUT = "timeout"        # Job processing timed out
    RETRYING = "retrying"      # Job is being retried
    BLOCKED = "blocked"        # Job is blocked by dependencies
    SKIPPED = "skipped"        # Job was skipped
    ARCHIVED = "archived"      # Job has been archived


class JobCategory(Enum):
    """Job categories for organization."""
    EVIDENCE = "evidence"      # Evidence-related jobs
    ANALYSIS = "analysis"      # Analysis jobs
    PROCESSING = "processing"  # Data processing jobs
    INVESTIGATION = "investigation"  # Investigation jobs
    REPORTING = "reporting"    # Reporting jobs
    SYSTEM = "system"          # System jobs
    CUSTOM = "custom"          # Custom jobs


@dataclass
class JobDependency:
    """Job dependency definition."""
    
    job_id: str
    dependency_type: str = "required"  # required, optional, exclusive
    condition: Optional[str] = None    # condition for dependency satisfaction
    timeout: Optional[timedelta] = None  # timeout for dependency wait
    
    def __post_init__(self):
        if not self.job_id:
            raise ValueError("Job dependency must have a job_id")


@dataclass
class JobResource:
    """Job resource requirement."""
    
    resource_type: str
    amount: float
    unit: str
    optional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobRetryPolicy:
    """Job retry policy configuration."""
    
    max_retries: int = 3
    retry_delay: timedelta = timedelta(minutes=5)
    backoff_multiplier: float = 2.0
    max_retry_delay: timedelta = timedelta(hours=1)
    retry_on_statuses: List[JobStatus] = field(default_factory=lambda: [JobStatus.FAILED, JobStatus.TIMEOUT])
    retry_on_exceptions: List[str] = field(default_factory=list)


@dataclass
class JobTimeout:
    """Job timeout configuration."""
    
    execution_timeout: timedelta = timedelta(hours=1)
    queue_timeout: timedelta = timedelta(hours=24)
    dependency_timeout: timedelta = timedelta(hours=12)
    cleanup_timeout: timedelta = timedelta(minutes=30)


@dataclass
class JobMetadata:
    """Job metadata and configuration."""
    
    case_id: Optional[str] = None
    investigator_id: Optional[str] = None
    organization_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    priority_boost: float = 1.0
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    cost_estimate: Optional[float] = None
    actual_cost: Optional[float] = None
    quality_score: Optional[float] = None
    confidence_score: Optional[float] = None


@dataclass
class JobResult:
    """Job execution result."""
    
    success: bool
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    execution_log: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)  # File paths or references


@dataclass
class Job:
    """
    Comprehensive job model for the forensic platform.
    
    This class represents a job that can be executed by the Taskmaster system.
    It includes all necessary information for job scheduling, execution, and monitoring.
    """
    
    # Core identification
    id: str
    name: str
    description: str
    job_type: JobType
    
    # Priority and scheduling
    priority: JobPriority = JobPriority.MEDIUM
    category: JobCategory = JobCategory.CUSTOM
    
    # Status and lifecycle
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Assignment and execution
    assigned_agent_id: Optional[str] = None
    assigned_agent_type: Optional[str] = None
    queue_name: Optional[str] = None
    
    # Dependencies and relationships
    dependencies: List[JobDependency] = field(default_factory=list)
    parent_job_id: Optional[str] = None
    child_job_ids: List[str] = field(default_factory=list)
    
    # Resource requirements
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    resource_resources: List[JobResource] = field(default_factory=list)
    
    # Configuration
    retry_policy: JobRetryPolicy = field(default_factory=JobRetryPolicy)
    timeout: JobTimeout = field(default_factory=JobTimeout)
    metadata: JobMetadata = field(default_factory=JobMetadata)
    
    # Execution
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Results and monitoring
    result: Optional[JobResult] = None
    progress: float = 0.0
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    
    # Retry and error handling
    retry_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    # Performance tracking
    queue_wait_time: Optional[timedelta] = None
    processing_time: Optional[timedelta] = None
    total_time: Optional[timedelta] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
        
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def update_status(self, new_status: JobStatus, **kwargs):
        """Update job status and related fields."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == JobStatus.RUNNING and not self.started_at:
            self.started_at = datetime.utcnow()
        elif new_status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            self.completed_at = datetime.utcnow()
        
        # Update other fields if provided
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_dependency(self, job_id: str, dependency_type: str = "required", 
                      condition: Optional[str] = None, timeout: Optional[timedelta] = None):
        """Add a dependency to this job."""
        dependency = JobDependency(
            job_id=job_id,
            dependency_type=dependency_type,
            condition=condition,
            timeout=timeout
        )
        self.dependencies.append(dependency)
    
    def remove_dependency(self, job_id: str):
        """Remove a dependency from this job."""
        self.dependencies = [dep for dep in self.dependencies if dep.job_id != job_id]
    
    def add_resource_requirement(self, resource_type: str, amount: float, unit: str = "units"):
        """Add a resource requirement to this job."""
        self.resource_requirements[resource_type] = amount
    
    def remove_resource_requirement(self, resource_type: str):
        """Remove a resource requirement from this job."""
        if resource_type in self.resource_requirements:
            del self.resource_requirements[resource_type]
    
    def can_start(self) -> bool:
        """Check if the job can start (dependencies satisfied)."""
        if not self.dependencies:
            return True
        
        # Check if all required dependencies are satisfied
        for dependency in self.dependencies:
            if dependency.dependency_type == "required":
                # This would check the actual dependency status
                # For now, return True
                pass
        
        return True
    
    def is_completed(self) -> bool:
        """Check if the job is completed."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def is_running(self) -> bool:
        """Check if the job is currently running."""
        return self.status == JobStatus.RUNNING
    
    def is_pending(self) -> bool:
        """Check if the job is pending execution."""
        return self.status in [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.ASSIGNED]
    
    def can_retry(self) -> bool:
        """Check if the job can be retried."""
        return (self.retry_count < self.retry_policy.max_retries and
                self.status in self.retry_policy.retry_on_statuses)
    
    def get_retry_delay(self) -> timedelta:
        """Calculate the delay before the next retry."""
        if self.retry_count == 0:
            return self.retry_policy.retry_delay
        
        delay = self.retry_policy.retry_delay * (self.retry_policy.backoff_multiplier ** self.retry_count)
        return min(delay, self.retry_policy.max_retry_delay)
    
    def get_priority_score(self) -> float:
        """Calculate the priority score for scheduling."""
        base_score = {
            JobPriority.CRITICAL: 1000,
            JobPriority.HIGH: 100,
            JobPriority.MEDIUM: 10,
            JobPriority.LOW: 1,
            JobPriority.BATCH: 5,
            JobPriority.MAINTENANCE: 2
        }.get(self.priority, 10)
        
        # Apply priority boost
        score = base_score * self.metadata.priority_boost
        
        # Adjust for age (older jobs get higher priority)
        age_hours = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        score += age_hours * 0.1
        
        # Adjust for retry count (failed jobs get higher priority)
        score += self.retry_count * 10
        
        return score
    
    def get_estimated_cost(self) -> float:
        """Get the estimated cost for this job."""
        if self.metadata.cost_estimate:
            return self.metadata.cost_estimate
        
        # Calculate based on job type and resource requirements
        base_cost = {
            JobType.EVIDENCE_COLLECTION: 10.0,
            JobType.EVIDENCE_ANALYSIS: 25.0,
            JobType.AI_ANALYSIS: 50.0,
            JobType.FRAUD_DETECTION: 75.0,
            JobType.RISK_ASSESSMENT: 40.0
        }.get(self.job_type, 20.0)
        
        # Adjust for priority
        priority_multiplier = {
            JobPriority.CRITICAL: 2.0,
            JobPriority.HIGH: 1.5,
            JobPriority.MEDIUM: 1.0,
            JobPriority.LOW: 0.8,
            JobPriority.BATCH: 0.7,
            JobPriority.MAINTENANCE: 0.5
        }.get(self.priority, 1.0)
        
        return base_cost * priority_multiplier
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'job_type': self.job_type.value,
            'priority': self.priority.value,
            'category': self.category.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'assigned_agent_id': self.assigned_agent_id,
            'queue_name': self.queue_name,
            'progress': self.progress,
            'retry_count': self.retry_count,
            'priority_score': self.get_priority_score(),
            'estimated_cost': self.get_estimated_cost()
        }
    
    def to_json(self) -> str:
        """Convert job to JSON representation."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create a job from dictionary representation."""
        # Convert enum values back
        if 'job_type' in data:
            data['job_type'] = JobType(data['job_type'])
        if 'priority' in data:
            data['priority'] = JobPriority(data['priority'])
        if 'category' in data:
            data['category'] = JobCategory(data['category'])
        if 'status' in data:
            data['status'] = JobStatus(data['status'])
        
        # Convert datetime strings back
        for field in ['created_at', 'updated_at', 'started_at', 'completed_at']:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)


# Job factory functions for common job types
def create_evidence_collection_job(
    name: str,
    description: str,
    case_id: str,
    investigator_id: str,
    priority: JobPriority = JobPriority.HIGH
) -> Job:
    """Create an evidence collection job."""
    return Job(
        name=name,
        description=description,
        job_type=JobType.EVIDENCE_COLLECTION,
        priority=priority,
        category=JobCategory.EVIDENCE,
        metadata=JobMetadata(
            case_id=case_id,
            investigator_id=investigator_id,
            tags=["evidence", "collection"],
            estimated_duration=timedelta(hours=2)
        )
    )


def create_ai_analysis_job(
    name: str,
    description: str,
    case_id: str,
    input_data: Dict[str, Any],
    priority: JobPriority = JobPriority.MEDIUM
) -> Job:
    """Create an AI analysis job."""
    return Job(
        name=name,
        description=description,
        job_type=JobType.AI_ANALYSIS,
        priority=priority,
        category=JobCategory.ANALYSIS,
        input_data=input_data,
        metadata=JobMetadata(
            case_id=case_id,
            tags=["ai", "analysis", "ml"],
            estimated_duration=timedelta(hours=4),
            cost_estimate=50.0
        ),
        resource_requirements={
            'gpu_memory': 8.0,
            'cpu_cores': 4.0,
            'memory': 16.0
        }
    )


def create_fraud_detection_job(
    name: str,
    description: str,
    case_id: str,
    transaction_data: Dict[str, Any],
    priority: JobPriority = JobPriority.HIGH
) -> Job:
    """Create a fraud detection job."""
    return Job(
        name=name,
        description=description,
        job_type=JobType.FRAUD_DETECTION,
        priority=priority,
        category=JobCategory.ANALYSIS,
        input_data=transaction_data,
        metadata=JobMetadata(
            case_id=case_id,
            tags=["fraud", "detection", "financial"],
            estimated_duration=timedelta(hours=6),
            cost_estimate=75.0
        ),
        resource_requirements={
            'cpu_cores': 8.0,
            'memory': 32.0,
            'storage': 100.0
        }
    )


def create_batch_processing_job(
    name: str,
    description: str,
    file_list: List[str],
    priority: JobPriority = JobPriority.BATCH
) -> Job:
    """Create a batch processing job."""
    return Job(
        name=name,
        description=description,
        job_type=JobType.BATCH_PROCESSING,
        priority=priority,
        category=JobCategory.PROCESSING,
        input_data={'files': file_list},
        metadata=JobMetadata(
            tags=["batch", "processing"],
            estimated_duration=timedelta(hours=8),
            cost_estimate=30.0
        ),
        resource_requirements={
            'cpu_cores': 2.0,
            'memory': 8.0,
            'storage': 50.0
        }
    )


# Example usage and testing
if __name__ == "__main__":
    # Create sample jobs
    evidence_job = create_evidence_collection_job(
        "Collect Bank Statements",
        "Collect and verify bank statements for case ABC-123",
        "case_001",
        "investigator_001",
        JobPriority.HIGH
    )
    
    ai_job = create_ai_analysis_job(
        "Analyze Transaction Patterns",
        "Use AI to detect suspicious transaction patterns",
        "case_001",
        {"transactions": [1, 2, 3, 4, 5]},
        JobPriority.MEDIUM
    )
    
    fraud_job = create_fraud_detection_job(
        "Detect Money Laundering",
        "Analyze transactions for money laundering patterns",
        "case_001",
        {"transactions": [1, 2, 3, 4, 5]},
        JobPriority.CRITICAL
    )
    
    # Print job information
    print("Evidence Collection Job:")
    print(f"  ID: {evidence_job.id}")
    print(f"  Priority Score: {evidence_job.get_priority_score()}")
    print(f"  Estimated Cost: ${evidence_job.get_estimated_cost():.2f}")
    
    print("\nAI Analysis Job:")
    print(f"  ID: {ai_job.id}")
    print(f"  Priority Score: {ai_job.get_priority_score()}")
    print(f"  Estimated Cost: ${ai_job.get_estimated_cost():.2f}")
    
    print("\nFraud Detection Job:")
    print(f"  ID: {fraud_job.id}")
    print(f"  Priority Score: {fraud_job.get_priority_score()}")
    print(f"  Estimated Cost: ${fraud_job.get_estimated_cost():.2f}")
    
    print("\nJob system initialized successfully!")

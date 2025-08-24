Job Model - Comprehensive Job Management System

This module defines the Job model and related components for the Taskmaster system,
including all job types, priorities, and statuses needed for forensic investigations.

import json
import uuid
from datetime import datetime, timedelta

class JobType(Enum):

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

    CRITICAL = "critical"  # Immediate attention required
    HIGH = "high"  # High priority, process soon
    MEDIUM = "medium"  # Normal priority
    LOW = "low"  # Low priority, process when possible
    BATCH = "batch"  # Batch processing priority
    MAINTENANCE = "maintenance"  # System maintenance priority

class JobStatus(Enum):

    PENDING = "pending"  # Job is waiting to be processed
    QUEUED = "queued"  # Job is in processing queue
    ASSIGNED = "assigned"  # Job has been assigned to an agent
    RUNNING = "running"  # Job is currently being processed
    PAUSED = "paused"  # Job processing has been paused
    RESUMED = "resumed"  # Job processing has been resumed
    COMPLETED = "completed"  # Job has been completed successfully
    FAILED = "failed"  # Job processing failed
    CANCELLED = "cancelled"  # Job has been cancelled
    TIMEOUT = "timeout"  # Job processing timed out
    RETRYING = "retrying"  # Job is being retried
    BLOCKED = "blocked"  # Job is blocked by dependencies
    SKIPPED = "skipped"  # Job was skipped
    ARCHIVED = "archived"  # Job has been archived

class JobCategory(Enum):

    EVIDENCE = "evidence"  # Evidence-related jobs
    ANALYSIS = "analysis"  # Analysis jobs
    PROCESSING = "processing"  # Data processing jobs
    INVESTIGATION = "investigation"  # Investigation jobs
    REPORTING = "reporting"  # Reporting jobs
    SYSTEM = "system"  # System jobs
    CUSTOM = "custom"  # Custom jobs

@dataclass
class JobDependency:

    dependency_type: str = "required"  # required, optional, exclusive
    condition: Optional[str] = None  # condition for dependency satisfaction
    timeout: Optional[timedelta] = None  # timeout for dependency wait

    def __post_init__(self):

            raise ValueError("Job dependency must have a job_id")

@dataclass
class JobResource:

        dependency_type: str = "required",
        condition: Optional[str] = None,
        timeout: Optional[timedelta] = None,
    ):

        self, resource_type: str, amount: float, unit: str = "units"
    ):

            if dependency.dependency_type == "required":
                # This would check the actual dependency status
                # For now, return True
                pass

        return True

    def is_completed(self) -> bool:

            "id": self.id,
            "name": self.name,
            "description": self.description,
            "job_type": self.job_type.value,
            "priority": self.priority.value,
            "category": self.category.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "assigned_agent_id": self.assigned_agent_id,
            "queue_name": self.queue_name,
            "progress": self.progress,
            "retry_count": self.retry_count,
            "priority_score": self.get_priority_score(),
            "estimated_cost": self.get_estimated_cost(),
        }

    def to_json(self) -> str:

    def from_dict(cls, data: Dict[str, Any]) -> "Job":

        if "job_type" in data:
            data["job_type"] = JobType(data["job_type"])
        if "priority" in data:
            data["priority"] = JobPriority(data["priority"])
        if "category" in data:
            data["category"] = JobCategory(data["category"])
        if "status" in data:
            data["status"] = JobStatus(data["status"])

        # Convert datetime strings back
        for field in ["created_at", "updated_at", "started_at", "completed_at"]:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)

# Job factory functions for common job types
def create_evidence_collection_job(
    name: str,
    description: str,
    case_id: str,
    investigator_id: str,
    priority: JobPriority = JobPriority.HIGH,
) -> Job:

            tags=["evidence", "collection"],
            estimated_duration=timedelta(hours=2),
        ),
    )

def create_ai_analysis_job(
    name: str,
    description: str,
    case_id: str,
    input_data: Dict[str, Any],
    priority: JobPriority = JobPriority.MEDIUM,
) -> Job:

            tags=["ai", "analysis", "ml"],
            estimated_duration=timedelta(hours=4),
            cost_estimate=50.0,
        ),
        resource_requirements={"gpu_memory": 8.0, "cpu_cores": 4.0, "memory": 16.0},
    )

def create_fraud_detection_job(
    name: str,
    description: str,
    case_id: str,
    transaction_data: Dict[str, Any],
    priority: JobPriority = JobPriority.HIGH,
) -> Job:

            tags=["fraud", "detection", "financial"],
            estimated_duration=timedelta(hours=6),
            cost_estimate=75.0,
        ),
        resource_requirements={"cpu_cores": 8.0, "memory": 32.0, "storage": 100.0},
    )

def create_batch_processing_job(
    name: str,
    description: str,
    file_list: List[str],
    priority: JobPriority = JobPriority.BATCH,
) -> Job:

        input_data={"files": file_list},
        metadata=JobMetadata(
            tags=["batch", "processing"],
            estimated_duration=timedelta(hours=8),
            cost_estimate=30.0,
        ),
        resource_requirements={"cpu_cores": 2.0, "memory": 8.0, "storage": 50.0},
    )

# Example usage and testing
if __name__ == "__main__":
    # Create sample jobs
    evidence_job = create_evidence_collection_job(
        "Collect Bank Statements",
        "Collect and verify bank statements for case ABC-123",
        "case_001",
        "investigator_001",
        JobPriority.HIGH,
    )

    ai_job = create_ai_analysis_job(
        "Analyze Transaction Patterns",
        "Use AI to detect suspicious transaction patterns",
        "case_001",
        {"transactions": [1, 2, 3, 4, 5]},
        JobPriority.MEDIUM,
    )

    fraud_job = create_fraud_detection_job(
        "Detect Money Laundering",
        "Analyze transactions for money laundering patterns",
        "case_001",
        {"transactions": [1, 2, 3, 4, 5]},
        JobPriority.CRITICAL,
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

Taskmaster Data Models

This package contains all the data models used by the Taskmaster system
for job assignment, workflow management, and resource allocation.

from .job import Job, JobPriority, JobResult, JobStatus, JobType

__all__ = [
    # Job models
    "Job",
    "JobStatus",
    "JobPriority",
    "JobType",
    "JobResult",
]

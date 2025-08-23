"""
Taskmaster Core Components Package

This package contains the core components of the Taskmaster system:
- Job scheduling and management
- Task routing and distribution
- Workflow orchestration
- Resource monitoring and health management
"""

# Core Taskmaster components
from .job_scheduler import JobScheduler
from .resource_monitor import ResourceMonitor
from .task_router import TaskRouter
from .taskmaster import Taskmaster
from .workflow_orchestrator import WorkflowOrchestrator

__version__ = "1.0.0"
__author__ = "Forensic Reconciliation Platform Team"

__all__ = [
    "JobScheduler",
    "TaskRouter",
    "WorkflowOrchestrator",
    "ResourceMonitor",
    "Taskmaster",
]

# Initialize logging when package is imported
import logging

logging.getLogger(__name__).info(
    "Taskmaster Core Components package initialized v1.0.0"
)

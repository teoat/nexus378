"""
Taskmaster System - Job Assignment & Workflow Management

The Taskmaster System is the central orchestration engine for the Forensic 
Reconciliation + Fraud Platform, responsible for job assignment, workflow 
management, resource allocation, and task execution monitoring.
"""

__version__ = "1.0.0"
__author__ = "Forensic Reconciliation Platform Team"
__description__ = "Intelligent job assignment and workflow orchestration system"

from .core.taskmaster import Taskmaster
from .core.job_scheduler import JobScheduler
from .core.task_router import TaskRouter
from .core.workflow_orchestrator import WorkflowOrchestrator
from .core.resource_monitor import ResourceMonitor

__all__ = [
    "Taskmaster",
    "JobScheduler", 
    "TaskRouter",
    "WorkflowOrchestrator",
    "ResourceMonitor"
]

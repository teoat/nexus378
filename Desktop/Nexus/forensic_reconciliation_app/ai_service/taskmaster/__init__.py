"""
Taskmaster System - Job Assignment & Workflow Management

The Taskmaster System is the central orchestration engine for the Forensic 
Reconciliation + Fraud Platform, responsible for job assignment, workflow 
management, resource allocation, and task execution monitoring.
"""

__version__ = "1.0.0"
__author__ = "Forensic Reconciliation Platform Team"
__description__ = "Intelligent job assignment and workflow orchestration system"

# NOTE: The following imports are commented out because they refer to modules
# that do not exist in the current codebase (e.g., 'taskmaster.py', 'job_scheduler.py').
# Their functionality is implemented in other files like 'mcp_server.py'.
# Leaving these imports active was causing ModuleNotFoundError and breaking
# the test discovery process for this package.

# from .core.taskmaster import Taskmaster
# from .core.job_scheduler import JobScheduler
# from .core.task_router import TaskRouter
# from .core.workflow_orchestrator import WorkflowOrchestrator
# from .core.resource_monitor import ResourceMonitor

# __all__ = [
#     "Taskmaster",
#     "JobScheduler",
#     "TaskRouter",
#     "WorkflowOrchestrator",
#     "ResourceMonitor"
# ]

"""
Taskmaster - Main Coordination Engine

This module implements the main Taskmaster class that coordinates
all components of the task management system.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import asyncio

from ..models.job import Job, JobStatus
from .production_task_system import UnifiedTaskSystem
from .resource_monitor import ResourceMonitor
from .task_router import TaskRouter
from .workflow_orchestrator import WorkflowOrchestrator


class SystemStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class SystemMetrics:
    total_jobs_processed: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    system_health: str
    uptime_seconds: float
    last_updated: datetime


class Taskmaster:
    """
    Main Taskmaster coordination engine.

    The Taskmaster coordinates:
    - Job scheduling and execution
    - Task routing to agents
    - Workflow orchestration
    - Resource monitoring
    - System health management
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Taskmaster system."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.max_workers = config.get("max_workers", 10)
        self.enable_monitoring = config.get("enable_monitoring", True)
        self.auto_scaling = config.get("auto_scaling", True)

        # System state
        self.status = SystemStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self.uptime_start: Optional[datetime] = None

        # Core components
        self.unified_task_system: Optional[UnifiedTaskSystem] = None
        self.task_router: Optional[TaskRouter] = None
        self.workflow_orchestrator: Optional[WorkflowOrchestrator] = None
        self.resource_monitor: Optional[ResourceMonitor] = None

        # Metrics
        self.total_jobs_processed = 0
        self.active_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs = 0

        # Background tasks
        self.monitor_task: Optional[asyncio.Task] = None

        self.logger.info("Taskmaster initialized successfully")

    async def start(self):
        """Start the Taskmaster system."""
        try:
            self.logger.info("Starting Taskmaster system...")
            self.status = SystemStatus.STARTING

            # Initialize core components
            await self._initialize_components()

            # Start components
            await self._start_components()

            # Start monitoring
            if self.enable_monitoring:
                await self._start_monitoring()

            # Update status
            self.status = SystemStatus.RUNNING
            self.start_time = datetime.utcnow()
            self.uptime_start = datetime.utcnow()

            self.logger.info("Taskmaster system started successfully")

        except Exception as e:
            self.logger.error(f"Error starting Taskmaster: {e}")
            self.status = SystemStatus.ERROR
            raise

    async def stop(self):
        """Stop the Taskmaster system."""
        try:
            self.logger.info("Stopping Taskmaster system...")
            self.status = SystemStatus.STOPPING

            # Stop monitoring
            if self.monitor_task:
                self.monitor_task.cancel()

            # Stop components
            await self._stop_components()

            # Update status
            self.status = SystemStatus.STOPPED

            self.logger.info("Taskmaster system stopped successfully")

        except Exception as e:
            self.logger.error(f"Error stopping Taskmaster: {e}")
            self.status = SystemStatus.ERROR
            raise

    async def submit_job(self, job: Job) -> str:
        """Submit a job for processing using UnifiedTaskSystem."""
        try:
            if self.status != SystemStatus.RUNNING:
                raise RuntimeError("Taskmaster system is not running")

            if not self.unified_task_system:
                raise RuntimeError("UnifiedTaskSystem not initialized")

            # Submit job to UnifiedTaskSystem
            task_id = self.unified_task_system.add_new_todo(
                name=job.job_type.value,
                description=job.parameters.get("description", "No description"),
                priority=job.priority.value,
                estimated_duration="2-4 hours",  # Placeholder
                required_capabilities=job.parameters.get(
                    "required_capabilities", ["general"]
                ),
            )

            self.logger.info(f"Job {task_id} submitted successfully")
            return task_id

        except Exception as e:
            self.logger.error(f"Error submitting job: {e}")
            raise

    async def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed job from UnifiedTaskSystem."""
        try:
            if not self.unified_task_system:
                return None

            task = self.unified_task_system.tasks.get(job_id)
            if not task:
                return {"job_id": job_id, "status": "not_found"}

            return {
                "job_id": task.id,
                "status": task.status.value,
                "progress": task.progress,
                "result": (
                    task.implementation_notes[-1]
                    if task.implementation_notes
                    else "In progress"
                ),
            }

        except Exception as e:
            self.logger.error(f"Error getting job result for {job_id}: {e}")
            return None

    async def get_system_status(self) -> SystemStatus:
        """Get current system status."""
        return self.status

    async def get_system_metrics(self) -> SystemMetrics:
        """Get comprehensive system metrics."""
        try:
            # Calculate uptime
            uptime_seconds = 0.0
            if self.uptime_start:
                uptime_seconds = (datetime.utcnow() - self.uptime_start).total_seconds()

            # Get metrics from UnifiedTaskSystem
            system_status = (
                self.unified_task_system.get_system_status()
                if self.unified_task_system
                else {}
            )
            system_health = "unknown"
            if self.resource_monitor:
                health = await self.resource_monitor.get_system_health()
                system_health = health.overall_status.value

            return SystemMetrics(
                total_jobs_processed=system_status.get("total_tasks", 0),
                active_jobs=system_status.get("in_progress_tasks", 0),
                completed_jobs=system_status.get("completed_tasks", 0),
                failed_jobs=system_status.get("failed_tasks", 0),
                system_health=system_health,
                uptime_seconds=uptime_seconds,
                last_updated=datetime.utcnow(),
            )

        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return SystemMetrics(
                total_jobs_processed=0,
                active_jobs=0,
                completed_jobs=0,
                failed_jobs=0,
                system_health="error",
                uptime_seconds=0.0,
                last_updated=datetime.utcnow(),
            )

    async def _initialize_components(self):
        """Initialize all core components."""
        try:
            # Initialize UnifiedTaskSystem
            db_path = self.config.get("db_path", "unified_tasks.db")
            self.unified_task_system = UnifiedTaskSystem(db_path)

            # Initialize task router
            router_config = self.config.get("router", {})
            self.task_router = TaskRouter(router_config)

            # Initialize workflow orchestrator
            workflow_config = self.config.get("workflow", {})
            self.workflow_orchestrator = WorkflowOrchestrator(workflow_config)

            # Initialize resource monitor
            monitor_config = self.config.get("monitor", {})
            self.resource_monitor = ResourceMonitor(monitor_config)

            self.logger.info("All core components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise

    async def _start_components(self):
        """Start all core components."""
        try:
            # UnifiedTaskSystem runs its background tasks on init, so no start() needed yet.

            # Start resource monitor
            if self.resource_monitor:
                await self.resource_monitor.start_monitoring()

            self.logger.info("All core components started successfully")

        except Exception as e:
            self.logger.error(f"Error starting components: {e}")
            raise

    async def _stop_components(self):
        """Stop all core components."""
        try:
            # UnifiedTaskSystem does not have a stop method yet.

            # Stop resource monitor
            if self.resource_monitor:
                await self.resource_monitor.stop_monitoring()

            self.logger.info("All core components stopped successfully")

        except Exception as e:
            self.logger.error(f"Error stopping components: {e}")
            raise

    async def _start_monitoring(self):
        """Start system monitoring."""
        try:
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            self.logger.info("System monitoring started")

        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            raise

    async def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            while self.status == SystemStatus.RUNNING:
                # Update metrics
                await self._update_metrics()

                # Check system health
                await self._check_system_health()

                # Wait for next monitoring cycle
                await asyncio.sleep(10)  # Monitor every 10 seconds

        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")

    async def _update_metrics(self):
        """Update system metrics."""
        # This is now handled by get_system_metrics directly from UnifiedTaskSystem
        pass

    async def _check_system_health(self):
        """Check overall system health."""
        try:
            if self.resource_monitor:
                health = await self.resource_monitor.get_system_health()

                if health.overall_status.value == "critical":
                    self.logger.critical(
                        "System health critical - immediate attention required"
                    )
                elif health.overall_status.value == "warning":
                    self.logger.warning("System health warning - monitoring closely")

        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")

    def register_agent(self, agent_id: str, capabilities: List[str]):
        """Register an agent with the task router."""
        try:
            if self.task_router:
                self.task_router.register_agent(agent_id, capabilities)
                self.logger.info(f"Agent {agent_id} registered successfully")

            if self.resource_monitor:
                self.resource_monitor.register_agent(agent_id)

        except Exception as e:
            self.logger.error(f"Error registering agent {agent_id}: {e}")

    def get_component_status(self) -> Dict[str, str]:
        """Get status of all components."""
        return {
            "taskmaster": self.status.value,
            "unified_task_system": (
                "running" if self.unified_task_system else "not_initialized"
            ),
            "task_router": "initialized" if self.task_router else "not_initialized",
            "workflow_orchestrator": (
                "initialized" if self.workflow_orchestrator else "not_initialized"
            ),
            "resource_monitor": (
                self.resource_monitor.status.value
                if self.resource_monitor
                else "not_initialized"
            ),
        }


# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        "max_workers": 10,
        "enable_monitoring": True,
        "auto_scaling": True,
        "scheduler": {"max_concurrent_jobs": 100, "default_strategy": "priority"},
        "router": {"routing_strategy": "hybrid"},
        "monitor": {"monitoring_interval": 5.0},
    }

    # Initialize Taskmaster
    taskmaster = Taskmaster(config)

    print("Taskmaster system initialized successfully!")

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
from .job_scheduler import JobScheduler
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
        self.job_scheduler: Optional[JobScheduler] = None
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
        """Submit a job for processing."""
        try:
            if self.status != SystemStatus.RUNNING:
                raise RuntimeError("Taskmaster system is not running")

            if not self.job_scheduler:
                raise RuntimeError("Job scheduler not initialized")

            # Submit job to scheduler
            job_id = await self.job_scheduler.schedule_job(job)

            # Update metrics
            self.total_jobs_processed += 1
            self.active_jobs += 1

            self.logger.info(f"Job {job_id} submitted successfully")
            return job_id

        except Exception as e:
            self.logger.error(f"Error submitting job: {e}")
            raise

    async def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed job."""
        try:
            if not self.job_scheduler:
                return None

            # Get job status
            status = await self.job_scheduler.get_job_status(job_id)

            if status == JobStatus.COMPLETED:
                # In a real implementation, this would return actual results
                return {
                    "job_id": job_id,
                    "status": status.value,
                    "result": "Job completed successfully",
                }
            elif status == JobStatus.FAILED:
                return {
                    "job_id": job_id,
                    "status": status.value,
                    "error": "Job failed during execution",
                }
            else:
                return {
                    "job_id": job_id,
                    "status": status.value if status else "unknown",
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

            # Get system health
            system_health = "unknown"
            if self.resource_monitor:
                health = await self.resource_monitor.get_system_health()
                system_health = health.overall_status.value

            return SystemMetrics(
                total_jobs_processed=self.total_jobs_processed,
                active_jobs=self.active_jobs,
                completed_jobs=self.completed_jobs,
                failed_jobs=self.failed_jobs,
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
            # Initialize job scheduler
            scheduler_config = self.config.get("scheduler", {})
            self.job_scheduler = JobScheduler(scheduler_config)

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
            # Start job scheduler
            if self.job_scheduler:
                await self.job_scheduler.start()

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
            # Stop job scheduler
            if self.job_scheduler:
                await self.job_scheduler.stop()

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
        try:
            if self.job_scheduler:
                # Get scheduler metrics
                scheduler_metrics = self.job_scheduler.get_metrics()

                # Update local metrics
                self.active_jobs = scheduler_metrics.active_jobs
                self.completed_jobs = scheduler_metrics.total_jobs_completed
                self.failed_jobs = scheduler_metrics.total_jobs_failed

        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

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
            "job_scheduler": (
                self.job_scheduler.status.value
                if self.job_scheduler
                else "not_initialized"
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

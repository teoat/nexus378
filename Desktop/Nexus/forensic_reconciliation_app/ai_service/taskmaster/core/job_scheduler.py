"""
Job Scheduler - Core Job Management and Scheduling System

This module implements the JobScheduler class that provides comprehensive
job scheduling, queuing, and execution management for the Taskmaster system.
"""

import heapq
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import asyncio

from ..models.job import Job, JobPriority, JobStatus, JobType


class SchedulerStatus(Enum):
    """Status of the job scheduler."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class ScheduleStrategy(Enum):
    """Job scheduling strategies."""

    FIFO = "fifo"  # First In, First Out
    PRIORITY = "priority"  # Priority-based scheduling
    ROUND_ROBIN = "round_robin"  # Round-robin scheduling
    WEIGHTED_FAIR = "weighted_fair"  # Weighted fair queuing
    DEADLINE_AWARE = "deadline_aware"  # Deadline-aware scheduling


@dataclass
class ScheduledJob:
    """A job that has been scheduled for execution."""

    job: Job
    scheduled_time: datetime
    priority_score: float
    deadline: Optional[datetime]
    dependencies: List[str]
    retry_count: int = 0
    max_retries: int = 3
    last_execution_attempt: Optional[datetime] = None
    execution_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SchedulerMetrics:
    """Metrics for the job scheduler."""

    total_jobs_scheduled: int = 0
    total_jobs_completed: int = 0
    total_jobs_failed: int = 0
    total_jobs_cancelled: int = 0
    average_scheduling_time: float = 0.0
    average_execution_time: float = 0.0
    queue_length: int = 0
    active_jobs: int = 0
    failed_jobs: int = 0
    retry_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class JobScheduler:
    """
    Comprehensive job scheduling and management system.

    The JobScheduler provides:
    - Priority-based job scheduling
    - Dependency management
    - Retry mechanisms
    - Resource allocation
    - Performance monitoring
    - Deadline management
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the JobScheduler."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.max_concurrent_jobs = config.get("max_concurrent_jobs", 100)
        self.default_strategy = ScheduleStrategy(
            config.get("default_strategy", "priority")
        )
        self.enable_retries = config.get("enable_retries", True)
        self.max_retry_attempts = config.get("max_retry_attempts", 3)
        self.retry_delay_base = config.get("retry_delay_base", 1.0)
        self.enable_deadline_awareness = config.get("enable_deadline_awareness", True)

        # State management
        self.status = SchedulerStatus.STOPPED
        self.scheduled_jobs: Dict[str, ScheduledJob] = {}
        self.priority_queue: List[tuple] = []
        self.running_jobs: Dict[str, Job] = {}
        self.completed_jobs: Dict[str, Job] = {}
        self.failed_jobs: Dict[str, Job] = {}

        # Metrics
        self.metrics = SchedulerMetrics()

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Background tasks
        self.scheduler_task: Optional[asyncio.Task] = None
        self.monitor_task: Optional[asyncio.Task] = None

        # Callbacks
        self.job_execution_callback: Optional[Callable] = None
        self.job_completion_callback: Optional[Callable] = None
        self.job_failure_callback: Optional[Callable] = None

        self.logger.info("JobScheduler initialized successfully")

    async def start(self):
        """Start the job scheduler."""
        try:
            self.logger.info("Starting JobScheduler...")
            self.status = SchedulerStatus.STARTING

            # Start background tasks
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            self.monitor_task = asyncio.create_task(self._monitor_loop())

            self.status = SchedulerStatus.RUNNING
            self.logger.info("JobScheduler started successfully")

        except Exception as e:
            self.logger.error(f"Error starting JobScheduler: {e}")
            self.status = SchedulerStatus.ERROR
            raise

    async def stop(self):
        """Stop the job scheduler."""
        try:
            self.logger.info("Stopping JobScheduler...")
            self.status = SchedulerStatus.STOPPING

            # Cancel background tasks
            if self.scheduler_task:
                self.scheduler_task.cancel()
            if self.monitor_task:
                self.monitor_task.cancel()

            # Wait for tasks to complete
            await asyncio.gather(
                *[self.scheduler_task, self.monitor_task], return_exceptions=True
            )

            self.status = SchedulerStatus.STOPPED
            self.logger.info("JobScheduler stopped successfully")

        except Exception as e:
            self.logger.error(f"Error stopping JobScheduler: {e}")
            self.status = SchedulerStatus.ERROR
            raise

    async def schedule_job(self, job: Job) -> str:
        """Schedule a job for execution."""
        try:
            # Validate job
            if not self._validate_job(job):
                raise ValueError(f"Invalid job: {job.job_id}")

            # Create scheduled job
            scheduled_job = ScheduledJob(
                job=job,
                scheduled_time=datetime.utcnow(),
                priority_score=self._calculate_priority_score(job),
                deadline=job.deadline,
                dependencies=job.dependencies or [],
                max_retries=self.max_retry_attempts,
            )

            # Check dependencies
            if not await self._check_dependencies(scheduled_job):
                # Schedule for later when dependencies are met
                self._schedule_delayed_job(scheduled_job)
                return job.job_id

            # Add to priority queue
            self._add_to_queue(scheduled_job)

            # Store scheduled job
            self.scheduled_jobs[job.job_id] = scheduled_job

            # Update metrics
            self.metrics.total_jobs_scheduled += 1
            self.metrics.queue_length = len(self.priority_queue)

            self.logger.info(f"Job {job.job_id} scheduled successfully")
            return job.job_id

        except Exception as e:
            self.logger.error(f"Error scheduling job {job.job_id}: {e}")
            raise

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled or running job."""
        try:
            if job_id in self.scheduled_jobs:
                # Remove from scheduled jobs
                del self.scheduled_jobs[job_id]

                # Remove from priority queue
                self._remove_from_queue(job_id)

                # Update metrics
                self.metrics.total_jobs_cancelled += 1
                self.metrics.queue_length = len(self.priority_queue)

                self.logger.info(f"Job {job_id} cancelled successfully")
                return True

            elif job_id in self.running_jobs:
                # Mark as cancelled (will be handled by executor)
                job = self.running_jobs[job_id]
                job.status = JobStatus.CANCELLED

                # Update metrics
                self.metrics.total_jobs_cancelled += 1

                self.logger.info(f"Running job {job_id} marked as cancelled")
                return True

            else:
                self.logger.warning(f"Job {job_id} not found for cancellation")
                return False

        except Exception as e:
            self.logger.error(f"Error cancelling job {job_id}: {e}")
            return False

    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the current status of a job."""
        try:
            if job_id in self.scheduled_jobs:
                return JobStatus.PENDING
            elif job_id in self.running_jobs:
                return self.running_jobs[job_id].status
            elif job_id in self.completed_jobs:
                return JobStatus.COMPLETED
            elif job_id in self.failed_jobs:
                return JobStatus.FAILED
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error getting job status for {job_id}: {e}")
            return None

    async def list_pending_jobs(self) -> List[Job]:
        """Get a list of all pending jobs."""
        try:
            pending_jobs = []
            for scheduled_job in self.scheduled_jobs.values():
                if scheduled_job.job.status == JobStatus.PENDING:
                    pending_jobs.append(scheduled_job.job)
            return pending_jobs

        except Exception as e:
            self.logger.error(f"Error listing pending jobs: {e}")
            return []

    async def process_job_queue(self):
        """Process the job queue and execute ready jobs."""
        try:
            while (
                self.priority_queue
                and len(self.running_jobs) < self.max_concurrent_jobs
            ):
                # Get next job from queue
                priority_score, scheduled_time, job_id = heapq.heappop(
                    self.priority_queue
                )

                if job_id not in self.scheduled_jobs:
                    continue

                scheduled_job = self.scheduled_jobs[job_id]

                # Check if job is still valid
                if not self._is_job_valid(scheduled_job):
                    del self.scheduled_jobs[job_id]
                    continue

                # Check dependencies again
                if not await self._check_dependencies(scheduled_job):
                    # Re-add to queue for later
                    self._add_to_queue(scheduled_job)
                    continue

                # Execute job
                await self._execute_job(scheduled_job)

        except Exception as e:
            self.logger.error(f"Error processing job queue: {e}")

    def _validate_job(self, job: Job) -> bool:
        """Validate a job before scheduling."""
        try:
            # Check required fields
            if not job.job_id or not job.job_type:
                return False

            # Check job type validity
            if job.job_type not in JobType:
                return False

            # Check priority validity
            if job.priority not in JobPriority:
                return False

            # Check status validity
            if job.status not in JobStatus:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating job: {e}")
            return False

    def _calculate_priority_score(self, job: Job) -> float:
        """Calculate priority score for job scheduling."""
        try:
            base_score = 0.0

            # Priority-based scoring
            if job.priority == JobPriority.HIGH:
                base_score += 1000
            elif job.priority == JobPriority.MEDIUM:
                base_score += 500
            elif job.priority == JobPriority.LOW:
                base_score += 100

            # Deadline awareness
            if self.enable_deadline_awareness and job.deadline:
                time_until_deadline = (job.deadline - datetime.utcnow()).total_seconds()
                if time_until_deadline > 0:
                    # Higher score for jobs closer to deadline
                    base_score += max(0, 1000 - time_until_deadline)

            # Job type priority
            if job.job_type in [JobType.FRAUD_DETECTION, JobType.RISK_ASSESSMENT]:
                base_score += 200  # Higher priority for critical analysis

            # Add timestamp for FIFO ordering within same priority
            base_score += time.time()

            return base_score

        except Exception as e:
            self.logger.error(f"Error calculating priority score: {e}")
            return 0.0

    async def _check_dependencies(self, scheduled_job: ScheduledJob) -> bool:
        """Check if all job dependencies are met."""
        try:
            if not scheduled_job.dependencies:
                return True

            for dep_id in scheduled_job.dependencies:
                dep_status = await self.get_job_status(dep_id)
                if dep_status != JobStatus.COMPLETED:
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking dependencies: {e}")
            return False

    def _add_to_queue(self, scheduled_job: ScheduledJob):
        """Add a job to the priority queue."""
        try:
            # Use negative priority score for heapq (min-heap)
            queue_entry = (
                -scheduled_job.priority_score,
                scheduled_job.scheduled_time.timestamp(),
                scheduled_job.job.job_id,
            )
            heapq.heappush(self.priority_queue, queue_entry)

        except Exception as e:
            self.logger.error(f"Error adding job to queue: {e}")

    def _remove_from_queue(self, job_id: str):
        """Remove a job from the priority queue."""
        try:
            # Rebuild queue without the specified job
            new_queue = []
            for entry in self.priority_queue:
                if entry[2] != job_id:
                    new_queue.append(entry)

            heapq.heapify(new_queue)
            self.priority_queue = new_queue

        except Exception as e:
            self.logger.error(f"Error removing job from queue: {e}")

    def _schedule_delayed_job(self, scheduled_job: ScheduledJob):
        """Schedule a job for later execution when dependencies are met."""
        try:
            # Store in scheduled jobs (will be checked later)
            self.scheduled_jobs[scheduled_job.job.job_id] = scheduled_job

            self.logger.info(
                f"Job {scheduled_job.job.job_id} scheduled for later execution"
            )

        except Exception as e:
            self.logger.error(f"Error scheduling delayed job: {e}")

    def _is_job_valid(self, scheduled_job: ScheduledJob) -> bool:
        """Check if a scheduled job is still valid."""
        try:
            # Check if job has been cancelled
            if scheduled_job.job.status == JobStatus.CANCELLED:
                return False

            # Check deadline
            if scheduled_job.deadline and datetime.utcnow() > scheduled_job.deadline:
                return False

            # Check retry limit
            if scheduled_job.retry_count >= scheduled_job.max_retries:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking job validity: {e}")
            return False

    async def _execute_job(self, scheduled_job: ScheduledJob):
        """Execute a scheduled job."""
        try:
            job = scheduled_job.job
            job.status = JobStatus.RUNNING
            job.start_time = datetime.utcnow()

            # Add to running jobs
            self.running_jobs[job.job_id] = job

            # Remove from scheduled jobs
            del self.scheduled_jobs[job.job_id]

            # Update metrics
            self.metrics.active_jobs = len(self.running_jobs)
            self.metrics.queue_length = len(self.priority_queue)

            # Execute job (placeholder - in real implementation would call actual executor)
            if self.job_execution_callback:
                await self.job_execution_callback(job)
            else:
                # Simulate execution
                await asyncio.sleep(0.1)
                job.status = JobStatus.COMPLETED
                job.end_time = datetime.utcnow()

            # Move to completed jobs
            self.completed_jobs[job.job_id] = job
            del self.running_jobs[job.job_id]

            # Update metrics
            self.metrics.total_jobs_completed += 1
            self.metrics.active_jobs = len(self.running_jobs)

            # Call completion callback
            if self.job_completion_callback:
                await self.job_completion_callback(job)

            self.logger.info(f"Job {job.job_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Error executing job {scheduled_job.job.job_id}: {e}")
            await self._handle_job_failure(scheduled_job, str(e))

    async def _handle_job_failure(self, scheduled_job: ScheduledJob, error: str):
        """Handle job execution failure."""
        try:
            job = scheduled_job.job
            job.status = JobStatus.FAILED
            job.end_time = datetime.utcnow()
            job.error_message = error

            # Increment retry count
            scheduled_job.retry_count += 1
            scheduled_job.last_execution_attempt = datetime.utcnow()

            # Record execution attempt
            execution_record = {
                "attempt": scheduled_job.retry_count,
                "timestamp": scheduled_job.last_execution_attempt.isoformat(),
                "error": error,
            }
            scheduled_job.execution_history.append(execution_record)

            # Remove from running jobs
            if job.job_id in self.running_jobs:
                del self.running_jobs[job.job_id]

            # Check if retry is possible
            if (
                scheduled_job.retry_count < scheduled_job.max_retries
                and self.enable_retries
            ):
                # Schedule retry with exponential backoff
                retry_delay = self.retry_delay_base * (
                    2 ** (scheduled_job.retry_count - 1)
                )
                scheduled_job.scheduled_time = datetime.utcnow() + timedelta(
                    seconds=retry_delay
                )

                # Re-add to queue
                self._add_to_queue(scheduled_job)
                self.scheduled_jobs[job.job_id] = scheduled_job

                self.logger.info(
                    f"Job {job.job_id} scheduled for retry {scheduled_job.retry_count}"
                )
            else:
                # Move to failed jobs
                self.failed_jobs[job.job_id] = job

                # Update metrics
                self.metrics.total_jobs_failed += 1
                self.metrics.failed_jobs = len(self.failed_jobs)

                # Call failure callback
                if self.job_failure_callback:
                    await self.job_failure_callback(job, error)

                self.logger.warning(
                    f"Job {job.job_id} failed permanently after {scheduled_job.retry_count} attempts"
                )

        except Exception as e:
            self.logger.error(f"Error handling job failure: {e}")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        try:
            while self.status == SchedulerStatus.RUNNING:
                await self.process_job_queue()
                await asyncio.sleep(0.1)  # Process every 100ms

        except asyncio.CancelledError:
            self.logger.info("Scheduler loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in scheduler loop: {e}")
            self.status = SchedulerStatus.ERROR

    async def _monitor_loop(self):
        """Monitoring loop for metrics and health checks."""
        try:
            while self.status == SchedulerStatus.RUNNING:
                await self._update_metrics()
                await asyncio.sleep(5)  # Update every 5 seconds

        except asyncio.CancelledError:
            self.logger.info("Monitor loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitor loop: {e}")

    async def _update_metrics(self):
        """Update scheduler metrics."""
        try:
            # Calculate retry rate
            total_attempts = sum(
                job.retry_count for job in self.scheduled_jobs.values()
            )
            total_jobs = (
                len(self.scheduled_jobs)
                + len(self.running_jobs)
                + len(self.completed_jobs)
                + len(self.failed_jobs)
            )

            if total_jobs > 0:
                self.metrics.retry_rate = total_attempts / total_jobs

            # Update queue length
            self.metrics.queue_length = len(self.priority_queue)

            # Update active jobs count
            self.metrics.active_jobs = len(self.running_jobs)

            # Update timestamp
            self.metrics.last_updated = datetime.utcnow()

        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    def get_metrics(self) -> SchedulerMetrics:
        """Get current scheduler metrics."""
        return self.metrics

    def get_status(self) -> SchedulerStatus:
        """Get current scheduler status."""
        return self.status

    def set_job_execution_callback(self, callback: Callable):
        """Set callback for job execution."""
        self.job_execution_callback = callback

    def set_job_completion_callback(self, callback: Callable):
        """Set callback for job completion."""
        self.job_completion_callback = callback

    def set_job_failure_callback(self, callback: Callable):
        """Set callback for job failure."""
        self.job_failure_callback = callback


# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        "max_concurrent_jobs": 100,
        "default_strategy": "priority",
        "enable_retries": True,
        "max_retry_attempts": 3,
        "retry_delay_base": 1.0,
        "enable_deadline_awareness": True,
    }

    # Initialize scheduler
    scheduler = JobScheduler(config)

    print("JobScheduler system initialized successfully!")

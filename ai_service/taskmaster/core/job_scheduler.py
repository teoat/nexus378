Job Scheduler - Core Job Management and Scheduling System

This module implements the JobScheduler class that provides comprehensive
job scheduling, queuing, and execution management for the Taskmaster system.

import asyncio
import heapq
import logging
import time
from datetime import datetime, timedelta

from ..models.job import Job, JobPriority, JobStatus, JobType

class SchedulerStatus(Enum):

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

class ScheduleStrategy(Enum):

    FIFO = "fifo"  # First In, First Out
    PRIORITY = "priority"  # Priority-based scheduling
    ROUND_ROBIN = "round_robin"  # Round-robin scheduling
    WEIGHTED_FAIR = "weighted_fair"  # Weighted fair queuing
    DEADLINE_AWARE = "deadline_aware"  # Deadline-aware scheduling

@dataclass
class ScheduledJob:

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

            self.logger.error(f"Error getting job status for {job_id}: {e}")
            return None

    async def list_pending_jobs(self) -> List[Job]:

            self.logger.error(f"Error listing pending jobs: {e}")
            return []

    async def process_job_queue(self):

            self.logger.error(f"Error processing job queue: {e}")

    def _validate_job(self, job: Job) -> bool:

            self.logger.error(f"Error validating job: {e}")
            return False

    def _calculate_priority_score(self, job: Job) -> float:

            self.logger.error(f"Error calculating priority score: {e}")
            return 0.0

    async def _check_dependencies(self, scheduled_job: ScheduledJob) -> bool:

            self.logger.error(f"Error checking dependencies: {e}")
            return False

    def _add_to_queue(self, scheduled_job: ScheduledJob):

            self.logger.error(f"Error adding job to queue: {e}")

    def _remove_from_queue(self, job_id: str):

            self.logger.error(f"Error removing job from queue: {e}")

    def _schedule_delayed_job(self, scheduled_job: ScheduledJob):

                f"Job {scheduled_job.job.job_id} scheduled for later execution"
            )

        except Exception as e:
            self.logger.error(f"Error scheduling delayed job: {e}")

    def _is_job_valid(self, scheduled_job: ScheduledJob) -> bool:

            self.logger.error(f"Error checking job validity: {e}")
            return False

    async def _execute_job(self, scheduled_job: ScheduledJob):

            self.logger.info(f"Job {job.job_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Error executing job {scheduled_job.job.job_id}: {e}")
            await self._handle_job_failure(scheduled_job, str(e))

    async def _handle_job_failure(self, scheduled_job: ScheduledJob, error: str):

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

            self.logger.info("Scheduler loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in scheduler loop: {e}")
            self.status = SchedulerStatus.ERROR

    async def _monitor_loop(self):

            self.logger.info("Monitor loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitor loop: {e}")

    async def _update_metrics(self):

            self.logger.error(f"Error updating metrics: {e}")

    def get_metrics(self) -> SchedulerMetrics:

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

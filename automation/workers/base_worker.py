import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkerStatus(Enum):
    """Enum for worker status."""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"

@dataclass
class WorkerHealth:
    """Dataclass for worker health metrics."""
    status: WorkerStatus = WorkerStatus.IDLE
    last_heartbeat: float = field(default_factory=time.time)
    error_count: int = 0
    error_message: str | None = None

@dataclass
class WorkerPerformance:
    """Dataclass for worker performance metrics."""
    tasks_processed: int = 0
    total_processing_time: float = 0.0
    avg_processing_time: float = 0.0

class BaseWorker:
    """
    Base class for all specialized workers in the automation system.
    Provides common functionality for lifecycle management, health monitoring,
    performance tracking, and error handling.
    """

    def __init__(self, name: str):
        self.name = name
        self.health = WorkerHealth()
        self.performance = WorkerPerformance()
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused by default

    async def start(self, task_coroutine: Callable[[], Coroutine[Any, Any, None]]):
        """
        Starts the worker and begins executing the given task coroutine in a loop.
        """
        if self.health.status in [WorkerStatus.RUNNING, WorkerStatus.PAUSED]:
            logger.warning(f"Worker {self.name} is already running.")
            return

        logger.info(f"Starting worker {self.name}...")
        self.health.status = WorkerStatus.RUNNING
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(task_coroutine))
        logger.info(f"Worker {self.name} started.")

    async def _run(self, task_coroutine: Callable[[], Coroutine[Any, Any, None]]):
        """The main execution loop for the worker."""
        while not self._stop_event.is_set():
            await self._pause_event.wait()
            try:
                start_time = time.time()

                await task_coroutine()

                end_time = time.time()
                self._update_performance(end_time - start_time)

                await self.heartbeat()
                await asyncio.sleep(1) # TODO: Make this configurable
            except Exception as e:
                self._handle_error(e)
                # Depending on the error, we might want to stop or pause
                await self.pause()

        self.health.status = WorkerStatus.STOPPED
        logger.info(f"Worker {self.name} event loop stopped.")


    async def stop(self):
        """
        Stops the worker gracefully.
        """
        if self.health.status == WorkerStatus.STOPPED:
            logger.warning(f"Worker {self.name} is already stopped.")
            return

        logger.info(f"Stopping worker {self.name}...")
        self.health.status = WorkerStatus.STOPPED
        self._stop_event.set()
        self._pause_event.set() # Unpause to allow loop to exit
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.error(f"Worker {self.name} did not stop gracefully within timeout.")
                self._task.cancel()
        logger.info(f"Worker {self.name} stopped.")

    async def pause(self):
        """
        Pauses the worker's execution.
        """
        if self.health.status == WorkerStatus.RUNNING:
            logger.info(f"Pausing worker {self.name}...")
            self.health.status = WorkerStatus.PAUSED
            self._pause_event.clear()
            logger.info(f"Worker {self.name} paused.")

    async def resume(self):
        """
        Resumes the worker's execution.
        """
        if self.health.status == WorkerStatus.PAUSED:
            logger.info(f"Resuming worker {self.name}...")
            self.health.status = WorkerStatus.RUNNING
            self._pause_event.set()
            logger.info(f"Worker {self.name} resumed.")

    async def heartbeat(self):
        """
        Updates the worker's heartbeat to indicate it's alive and healthy.
        """
        self.health.last_heartbeat = time.time()
        logger.debug(f"Worker {self.name} heartbeat updated.")

    def _update_performance(self, processing_time: float):
        """
        Updates the performance metrics for the worker.
        """
        self.performance.tasks_processed += 1
        self.performance.total_processing_time += processing_time
        self.performance.avg_processing_time = (
            self.performance.total_processing_time / self.performance.tasks_processed
        )

    def _handle_error(self, error: Exception):
        """
        Handles an error encountered by the worker.
        """
        logger.error(f"Worker {self.name} encountered an error: {error}", exc_info=True)
        self.health.status = WorkerStatus.ERROR
        self.health.error_count += 1
        self.health.error_message = str(error)

    def get_status(self) -> dict:
        """
        Returns the current status, health, and performance of the worker.
        """
        return {
            "name": self.name,
            "health": self.health.__dict__,
            "performance": self.performance.__dict__
        }

if __name__ == '__main__':
    # Example usage and test for the BaseWorker

    async def example_task():
        """An example async task for the worker to run."""
        print(f"Executing example task...")
        await asyncio.sleep(2)
        print(f"Example task finished.")

    async def main():
        worker = BaseWorker("ExampleWorker")

        # Start the worker
        await worker.start(example_task)
        await asyncio.sleep(5)

        # Pause the worker
        await worker.pause()
        print("Worker paused. Status:", worker.get_status())
        await asyncio.sleep(5)

        # Resume the worker
        await worker.resume()
        print("Worker resumed. Status:", worker.get_status())
        await asyncio.sleep(5)

        # Stop the worker
        await worker.stop()
        print("Worker stopped. Status:", worker.get_status())

    asyncio.run(main())

"""
Job Scheduler Component
"""
import asyncio
from typing import Dict, Any

from ..models.job import Job, JobStatus, JobResult, JobType

class JobScheduler:
    def __init__(self, config: Dict[str, Any], taskmaster):
        self.config = config
        self.taskmaster = taskmaster
        self.job_queue = []
        self.running = False

    async def start(self):
        self.running = True
        asyncio.create_task(self._process_jobs())

    async def stop(self):
        self.running = False

    async def _process_jobs(self):
        while self.running:
            if self.job_queue:
                job = self.job_queue.pop(0)
                await self._execute_job(job)
            else:
                await asyncio.sleep(1)

    async def _execute_job(self, job: Job):
        if job.job_type == JobType.TODO_SCANNING:
            await self.taskmaster.todo_scanner.scan_and_process_todos(job.data["root_directory"])
            job.status = JobStatus.COMPLETED
        else:
            # Find an agent to execute the job
            agent = await self.taskmaster.task_router.find_agent_for_job(job)
            if agent:
                result = await agent.process(job)
                job.result = result
                job.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
            else:
                job.status = JobStatus.FAILED
                job.result = JobResult(success=False, error_message="No suitable agent found")

    async def pause(self):
        pass

    async def resume(self):
        pass

    async def submit_job(self, job: Job) -> str:
        self.job_queue.append(job)
        return job.id

    async def get_job_status(self, job_id: str) -> JobStatus:
        for job in self.job_queue:
            if job.id == job_id:
                return job.status
        return None

    async def cancel_job(self, job_id: str) -> bool:
        for job in self.job_queue:
            if job.id == job_id:
                job.status = JobStatus.CANCELLED
                return True
        return False

    async def get_health(self) -> Dict[str, Any]:
        return {"healthy": True}

    async def get_metrics(self) -> Dict[str, Any]:
        return {"job_queue_size": len(self.job_queue)}

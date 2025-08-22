import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from .taskmaster import Taskmaster, TaskmasterConfig
from .job_scheduler import JobScheduler
from ..models.job import Job, JobType, JobPriority, JobStatus

class TestPriorityQueues(unittest.TestCase):

    def setUp(self):
        self.config = TaskmasterConfig()
        self.taskmaster = Taskmaster(self.config)
        self.job_scheduler = JobScheduler(self.config)
        self.taskmaster.job_scheduler = self.job_scheduler

    def test_priority_queues(self):
        low_prio_job = Job(id="job_low", job_type=JobType.GENERAL, priority=JobPriority.LOW, data={})
        high_prio_job = Job(id="job_high", job_type=JobType.GENERAL, priority=JobPriority.HIGH, data={})
        normal_prio_job = Job(id="job_normal", job_type=JobType.GENERAL, priority=JobPriority.NORMAL, data={})

        async def run_test():
            await self.job_scheduler.submit_job(low_prio_job)
            await self.job_scheduler.submit_job(high_prio_job)
            await self.job_scheduler.submit_job(normal_prio_job)

            # Check that jobs are in the correct queues
            self.assertEqual(len(self.job_scheduler.job_queues[JobPriority.LOW]), 1)
            self.assertEqual(len(self.job_scheduler.job_queues[JobPriority.HIGH]), 1)
            self.assertEqual(len(self.job_scheduler.job_queues[JobPriority.NORMAL]), 1)

            # This is a simplified test. A more comprehensive test would involve
            # mocking the agents and the scheduling loop to verify that the
            # high-priority job is processed first.
            # For now, we just check that the queues are populated correctly.

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()

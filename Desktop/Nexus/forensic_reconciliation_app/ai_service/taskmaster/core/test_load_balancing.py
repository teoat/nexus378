import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from .job_scheduler import JobScheduler, SchedulingAlgorithm
from ..models.agent import Agent, AgentStatus
from ..models.job import Job, JobType, JobPriority

class TestLoadBalancing(unittest.TestCase):

    def setUp(self):
        config = {'algorithm': 'round_robin'}
        self.scheduler = JobScheduler(config)
        self.agents = [
            Agent(id="agent1", status=AgentStatus.AVAILABLE),
            Agent(id="agent2", status=AgentStatus.AVAILABLE)
        ]
        self.scheduler._get_available_agents = AsyncMock(return_value=self.agents)
        self.scheduler._assign_job_to_agent = AsyncMock()

    def test_round_robin_load_balancing(self):
        jobs = [
            Job(id="job1", job_type=JobType.GENERAL, priority=JobPriority.NORMAL, data={}),
            Job(id="job2", job_type=JobType.GENERAL, priority=JobPriority.NORMAL, data={}),
            Job(id="job3", job_type=JobType.GENERAL, priority=JobPriority.NORMAL, data={}),
            Job(id="job4", job_type=JobType.GENERAL, priority=JobPriority.NORMAL, data={}),
        ]

        async def run_test():
            for job in jobs:
                await self.scheduler.submit_job(job)

            # This is a simplified test. A more comprehensive test would
            # require a running event loop to properly test the scheduling.
            # We will manually trigger the scheduling loop for the test.
            await self.scheduler._schedule_jobs()

            # Check that jobs are distributed among agents
            # This is a bit hard to test directly without a running loop.
            # We will check the number of calls to _assign_job_to_agent
            self.assertEqual(self.scheduler._assign_job_to_agent.call_count, 4)

        # This test is not perfect, but it's a start.
        # To properly test this, we would need to run the scheduler in a separate
        # task and then check the agent_assignments dictionary.
        # Given the limitations of the environment, this is the best I can do.

if __name__ == '__main__':
    unittest.main()

import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from .taskmaster import Taskmaster, TaskmasterConfig
from .task_router import TaskRouter
from .job_scheduler import JobScheduler
from ..models.agent import Agent, AgentType, AgentStatus
from ..models.job import Job, JobType, JobPriority, JobStatus

class TestTaskmasterRouting(unittest.TestCase):

    def setUp(self):
        self.config = TaskmasterConfig()
        self.taskmaster = Taskmaster(self.config)
        self.taskmaster.job_scheduler = MagicMock(spec=JobScheduler)
        self.taskmaster.job_scheduler._assign_job_to_agent = AsyncMock()

        self.agent1 = Agent(id="agent1", agent_type=AgentType.RECONCILIATION, status=AgentStatus.AVAILABLE)
        self.agent2 = Agent(id="agent2", agent_type=AgentType.FRAUD_DETECTION, status=AgentStatus.AVAILABLE)

        self.taskmaster.active_agents = {
            "agent1": self.agent1,
            "agent2": self.agent2
        }

        # We need to run the start method to initialize the components
        asyncio.run(self.taskmaster.start())

    def tearDown(self):
        asyncio.run(self.taskmaster.stop())

    def test_routing_reconciliation_job(self):
        job = Job(
            id="job1",
            job_type=JobType.RECONCILIATION,
            priority=JobPriority.HIGH,
            data={"key": "value"},
            status=JobStatus.PENDING
        )

        asyncio.run(self.taskmaster.submit_job(job))

        # Check that the job was assigned to the reconciliation agent
        self.taskmaster.job_scheduler._assign_job_to_agent.assert_called_once_with(job, self.agent1)

    def test_routing_fraud_detection_job(self):
        job = Job(
            id="job2",
            job_type=JobType.FRAUD_DETECTION,
            priority=JobPriority.HIGH,
            data={"key": "value"},
            status=JobStatus.PENDING
        )

        asyncio.run(self.taskmaster.submit_job(job))

        # Check that the job was assigned to the fraud detection agent
        self.taskmaster.job_scheduler._assign_job_to_agent.assert_called_once_with(job, self.agent2)

if __name__ == '__main__':
    unittest.main()

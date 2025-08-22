import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from .taskmaster import Taskmaster, TaskmasterConfig
from .workflow_orchestrator import WorkflowOrchestrator, Workflow, WorkflowStep, WorkflowExecutionMode, Job, JobStatus, JobType, JobPriority

class TestWorkflowOrchestrator(unittest.TestCase):

    def setUp(self):
        self.config = TaskmasterConfig()
        self.taskmaster = Taskmaster(self.config)
        self.taskmaster.job_scheduler = MagicMock()
        self.taskmaster.submit_job = AsyncMock()
        self.taskmaster.get_job_status = AsyncMock(return_value=JobStatus.COMPLETED)

        self.orchestrator = WorkflowOrchestrator(self.config, taskmaster=self.taskmaster)

        self.test_workflow = Workflow(
            id="test_workflow_1",
            name="Test Workflow",
            description="A test workflow with two steps.",
            steps=[
                WorkflowStep(id="step1", name="Step 1", step_type="test_step", agent_type="test_agent"),
                WorkflowStep(id="step2", name="Step 2", step_type="test_step", agent_type="test_agent", dependencies=["step1"]),
            ],
            execution_mode=WorkflowExecutionMode.SEQUENTIAL
        )
        self.orchestrator.workflows[self.test_workflow.id] = self.test_workflow

    @patch('uuid.uuid4', return_value='test-uuid')
    def test_start_and_run_workflow(self, mock_uuid):
        async def run_test():
            execution_id = await self.orchestrator.start_workflow(self.test_workflow.id)
            self.assertIsNotNone(execution_id)

            # This is a bit tricky to test without a running event loop.
            # We will manually trigger the execution for the test.
            await self.orchestrator._execute_workflow(execution_id)

            # Check that two jobs were submitted
            self.assertEqual(self.taskmaster.submit_job.call_count, 2)

            # Check the status of the workflow
            status = await self.orchestrator.get_workflow_status(execution_id)
            self.assertEqual(status, JobStatus.COMPLETED)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()

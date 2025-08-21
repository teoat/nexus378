import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from .workflow_orchestrator import WorkflowOrchestrator, Workflow, WorkflowStep, Job, JobStatus, JobRetryPolicy

class TestRetryPolicy(unittest.TestCase):

    def setUp(self):
        self.orchestrator = WorkflowOrchestrator(config={}, taskmaster=MagicMock())
        self.orchestrator._wait_for_job_completion = AsyncMock()

    def test_retry_policy(self):
        async def run_test():
            step = WorkflowStep(id="step1", name="Step 1", step_type="test_step")
            job = Job(id="job1", name="Test Job", description="", job_type="test", retry_policy=JobRetryPolicy(max_retries=1))

            self.orchestrator._create_step_job = AsyncMock(return_value=job)
            self.orchestrator._wait_for_job_completion.side_effect = [
                {'status': JobStatus.FAILED, 'error': 'Test error'},
                {'status': JobStatus.COMPLETED, 'outputs': {}}
            ]

            result = await self.orchestrator._execute_step("exec1", step)

            self.assertEqual(self.orchestrator._wait_for_job_completion.call_count, 2)
            self.assertEqual(result['status'], JobStatus.COMPLETED)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()

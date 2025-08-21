import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from .workflow_orchestrator import WorkflowOrchestrator, Workflow, WorkflowStep, JobStatus, WorkflowStatus

class TestErrorHandling(unittest.TestCase):

    def setUp(self):
        self.orchestrator = WorkflowOrchestrator(config={}, taskmaster=MagicMock())
        self.orchestrator._wait_for_job_completion = AsyncMock(return_value={'status': JobStatus.FAILED, 'error': 'Test error'})
        self.orchestrator._attempt_workflow_recovery = AsyncMock()

    def test_workflow_failure_and_recovery(self):
        async def run_test():
            step = WorkflowStep(id="step1", name="Step 1", step_type="test_step")
            workflow = Workflow(id="wf1", name="Test Workflow", steps=[step])
            self.orchestrator.workflows["wf1"] = workflow

            execution_id = await self.orchestrator.start_workflow("wf1")

            # Manually trigger execution for the test
            await self.orchestrator._execute_workflow(execution_id)

            # Check that the workflow failed
            status = await self.orchestrator.get_workflow_status(execution_id)
            self.assertEqual(status, WorkflowStatus.FAILED)

            # Check that recovery was attempted
            self.orchestrator._attempt_workflow_recovery.assert_called_once_with(execution_id)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()

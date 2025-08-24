import unittest
import os
from pathlib import Path
import sys
from unittest.mock import patch

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.production_task_system import UnifiedTaskSystem, TaskPriority, TaskStatus


class TestUnifiedTaskSystem(unittest.TestCase):

    def setUp(self):
        """Set up a new UnifiedTaskSystem for each test."""
        self.db_path = "test_unified_tasks.db"
        self.system = UnifiedTaskSystem(db_path=self.db_path)
        self.system.tasks.clear()
        self.system.workers.clear()
        self.system.task_queue.clear()

    def tearDown(self):
        """Clean up the database file after each test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_new_todo(self):
        """Test adding a new TODO."""
        task_id = self.system.add_new_todo(
            name="Test Task",
            description="A description",
            priority=TaskPriority.NORMAL.value,
            estimated_duration="1-2 hours",
            required_capabilities=["python"],
        )
        self.assertIn(task_id, self.system.tasks)
        self.assertEqual(self.system.tasks[task_id].name, "Test Task")
        self.assertEqual(self.system.tasks[task_id].status, TaskStatus.PENDING)
        self.assertIn(task_id, self.system.task_queue)

    def test_register_worker(self):
        """Test registering a new worker."""
        worker_id = "worker-1"
        self.system.register_worker(worker_id, "Test Worker", ["python", "testing"])
        self.assertIn(worker_id, self.system.workers)
        self.assertEqual(self.system.workers[worker_id].name, "Test Worker")
        self.assertEqual(
            self.system.workers[worker_id].capabilities, ["python", "testing"]
        )

    def test_claim_and_complete_task(self):
        """Test the full lifecycle of a task: claim and complete."""
        task_id = self.system.add_new_todo(
            name="Test Task",
            description="A description",
            priority=TaskPriority.HIGH.value,
            estimated_duration="1-2 hours",
            required_capabilities=["python"],
        )
        worker_id = "worker-1"
        self.system.register_worker(worker_id, "Test Worker", ["python"])

        # Test claiming the task
        claim_successful = self.system.claim_task(worker_id, task_id)
        self.assertTrue(claim_successful)
        self.assertEqual(self.system.tasks[task_id].status, TaskStatus.IN_PROGRESS)
        self.assertEqual(self.system.tasks[task_id].assigned_worker, worker_id)
        self.assertNotIn(task_id, self.system.task_queue)

        # Test completing the task
        complete_successful = self.system.complete_task(
            worker_id, task_id, "Completed successfully"
        )
        self.assertTrue(complete_successful)
        self.assertEqual(self.system.tasks[task_id].status, TaskStatus.COMPLETED)
        self.assertIn(task_id, self.system.completed_tasks)
        self.assertEqual(self.system.workers[worker_id].status, "idle")

    def test_fail_to_claim_task_in_progress(self):
        """Test that a worker cannot claim a task that is already in progress."""
        task_id = self.system.add_new_todo("Test Task", "", "normal", "1h", ["python"])
        worker1_id = "worker-1"
        worker2_id = "worker-2"
        self.system.register_worker(worker1_id, "Worker 1", ["python"])
        self.system.register_worker(worker2_id, "Worker 2", ["python"])

        # Worker 1 claims the task
        self.system.claim_task(worker1_id, task_id)

        # Worker 2 attempts to claim the same task
        claim_successful = self.system.claim_task(worker2_id, task_id)
        self.assertFalse(claim_successful)

    def test_fail_to_claim_task_insufficient_capabilities(self):
        """Test that a worker cannot claim a task if they lack capabilities."""
        task_id = self.system.add_new_todo("Test Task", "", "normal", "1h", ["java"])
        worker_id = "worker-1"
        self.system.register_worker(worker_id, "Python Worker", ["python"])

        claim_successful = self.system.claim_task(worker_id, task_id)
        self.assertFalse(claim_successful)

    def test_get_system_status(self):
        """Test getting the system status."""
        self.system.add_new_todo("Task 1", "", "normal", "1h", [])
        self.system.add_new_todo("Task 2", "", "normal", "1h", [])
        self.system.register_worker("worker-1", "Worker 1", [])

        status = self.system.get_system_status()
        self.assertEqual(status["total_tasks"], 2)
        self.assertEqual(status["pending_tasks"], 2)
        self.assertEqual(status["total_workers"], 1)


if __name__ == "__main__":
    unittest.main()

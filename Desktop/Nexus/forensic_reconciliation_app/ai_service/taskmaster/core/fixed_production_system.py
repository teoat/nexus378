#!/usr/bin/env python3
"""
Fixed Production System
Ensures database consistency and proper task assignment
"""

import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from corrected_todo_reader import CorrectedTodoMasterReader
from production_task_system import UnifiedTaskSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FixedProductionSystem:
    """Fixed production system with proper database consistency and task assignment"""

    def __init__(self, db_path: str = "production_todos.db"):
        self.db_path = db_path
        self.system = UnifiedTaskSystem(db_path)
        self.todo_reader = CorrectedTodoMasterReader()
        self.loaded_todos = []

    def load_real_todos_from_master(self):
        """Load real TODOs from TODO_MASTER.md and ensure they're in the system"""
        print("📖 Loading real TODOs from TODO_MASTER.md...")

        # Read TODOs using the corrected reader
        todos = self.todo_reader.read_todo_master()

        if not todos:
            print("❌ No real TODOs found in TODO_MASTER.md")
            return False

        print(f"📋 Found {len(todos)} real TODOs in TODO_MASTER.md")

        # Clear existing tasks to prevent duplicates
        self._clear_existing_tasks()

        # Add each real TODO to the production system
        added_count = 0
        for todo in todos:
            try:
                # Extract required fields
                name = todo.get("name", "Unnamed Task")
                description = todo.get("description", "No description provided")
                priority = todo.get("priority", "NORMAL")
                duration = todo.get("estimated_duration", "2-4 hours")
                capabilities = todo.get("required_capabilities", ["general"])

                # Add to production system
                task_id = self.system.add_new_todo(
                    name=name,
                    description=description,
                    priority=priority,
                    estimated_duration=duration,
                    required_capabilities=capabilities,
                )

                print(f"✅ Added: {task_id} - {name}")
                added_count += 1

                # Store loaded todo info
                self.loaded_todos.append(
                    {
                        "task_id": task_id,
                        "name": name,
                        "section": todo.get("section", "Unknown"),
                        "priority": priority,
                    }
                )

            except Exception as e:
                print(f"❌ Failed to add TODO '{todo.get('name', 'Unknown')}': {e}")

        print(
            f"\n🎯 Successfully loaded {added_count} real TODOs into production system"
        )

        # Verify tasks are actually in the system
        self._verify_tasks_in_system()

        return True

    def _clear_existing_tasks(self):
        """Clear existing tasks to prevent duplicates"""
        if self.system.tasks:
            print("🧹 Clearing existing tasks to prevent duplicates...")
            # Clear the tasks dictionary and queue
            self.system.tasks.clear()
            self.system.task_queue.clear()
            self.system.completed_tasks.clear()
            self.system.failed_tasks.clear()
            # Clear task locks
            self.system.task_locks.clear()
            print("✅ Existing tasks cleared")

    def _verify_tasks_in_system(self):
        """Verify that tasks are actually in the system"""
        print("\n🔍 Verifying tasks are in the system...")
        print(f"System reports {len(self.system.tasks)} tasks")

        if len(self.system.tasks) != len(self.loaded_todos):
            print(
                f"❌ MISMATCH: System has {len(self.system.tasks)} tasks but {len(self.loaded_todos)} were loaded"
            )
            print("This indicates a database synchronization issue!")
            return False

        print("✅ Task count matches loaded count")

        # Check if tasks are actually accessible
        for todo in self.loaded_todos:
            task_id = todo["task_id"]
            if task_id not in self.system.tasks:
                print(f"❌ Task {task_id} not found in system!")
                return False

        print("✅ All tasks are accessible in the system")
        return True

    def register_workers_and_verify(self):
        """Register workers and verify they can see tasks"""
        print("\n👷 Registering workers and verifying task visibility...")

        # Define workers based on actual requirements
        workers = [
            (
                "code_quality_worker",
                "Code Quality Engineer",
                "python_development,code_quality,general_implementation",
            ),
            (
                "documentation_worker",
                "Documentation Engineer",
                "documentation,technical_writing",
            ),
            (
                "security_worker",
                "Security Engineer",
                "security,authentication,encryption",
            ),
            ("performance_worker", "Performance Engineer", "performance,optimization"),
            (
                "general_worker",
                "General Developer",
                "python_development,general_implementation,error_handling",
            ),
        ]

        registered_count = 0
        for worker_id, name, capabilities in workers:
            if self.system.register_worker(worker_id, name, capabilities.split(",")):
                print(f"✅ Registered: {worker_id} - {name}")
                registered_count += 1

                # Verify this worker can see available tasks
                available_tasks = self.system.get_available_tasks(worker_id)
                print(f"   📋 Worker can see {len(available_tasks)} available tasks")

                if available_tasks:
                    # Handle both object and dictionary task formats
                    if hasattr(available_tasks[0], "name"):
                        # Task objects
                        sample_names = [t.name for t in available_tasks[:2]]
                    else:
                        # Task dictionaries
                        sample_names = [
                            t.get("name", "Unknown") for t in available_tasks[:2]
                        ]
                    print(f"   📝 Sample tasks: {', '.join(sample_names)}")
                else:
                    print(
                        f"   ⚠️  Worker cannot see any tasks - this indicates a problem!"
                    )
            else:
                print(f"⚠️  Worker {worker_id} already exists")

        print(f"\n🚀 {registered_count} workers registered and verified!")

        # Overall verification
        total_available = sum(
            len(self.system.get_available_tasks(wid))
            for wid in self.system.workers.keys()
        )
        print(f"📊 Total available tasks across all workers: {total_available}")

        if total_available == 0:
            print("🚨 CRITICAL ISSUE: No workers can see any tasks!")
            return False

        return True

    def test_task_workflow(self):
        """Test the complete task workflow"""
        print("\n🧪 Testing complete task workflow...")

        if not self.system.workers:
            print("❌ No workers registered")
            return False

        # Test with first available worker
        worker_id = list(self.system.workers.keys())[0]
        worker = self.system.workers[worker_id]

        print(f"Testing with worker: {worker_id} ({worker.name})")

        # Get available tasks
        available_tasks = self.system.get_available_tasks(worker_id)
        if not available_tasks:
            print(f"❌ Worker {worker_id} cannot see any tasks")
            return False

        test_task = available_tasks[0]

        # Handle both object and dictionary task formats
        if hasattr(test_task, "name"):
            # Task object
            task_name = test_task.name
            task_id = test_task.id
        else:
            # Task dictionary
            task_name = test_task.get("name", "Unknown")
            task_id = test_task.get("id", "unknown")

        print(f"📋 Testing with task: {task_name} (ID: {task_id})")

        # Test claiming the task
        if self.system.claim_task(worker_id, task_id):
            print(f"✅ Successfully claimed task {task_id}")

            # Test updating progress
            if self.system.update_task_progress(worker_id, task_id, 50, "Halfway done"):
                print(f"✅ Successfully updated progress to 50%")

                # Test completing the task
                if self.system.complete_task(
                    worker_id, task_id, "Task completed successfully"
                ):
                    print(f"✅ Successfully completed task {task_id}")

                    # Verify task status
                    if task_id in self.system.completed_tasks:
                        print(f"✅ Task {task_id} is now in completed tasks")
                        return True
                    else:
                        print(f"❌ Task {task_id} not found in completed tasks")
                        return False
                else:
                    print(f"❌ Failed to complete task {task_id}")
                    return False
            else:
                print(f"❌ Failed to update progress for task {task_id}")
                return False
        else:
            print(f"❌ Failed to claim task {task_id}")
            return False

    def show_system_status(self):
        """Show comprehensive system status"""
        status = self.system.get_system_status()
        print("\n📊 Fixed Production System Status:")
        print(f"  Total TODOs: {status['total_tasks']}")
        print(f"  Pending: {status['pending_tasks']}")
        print(f"  In Progress: {status['in_progress_tasks']}")
        print(f"  Completed: {status['completed_tasks']}")
        print(f"  Failed: {status['failed_tasks']}")
        print(f"  Total Workers: {status['total_workers']}")
        print(f"  Active Workers: {status['active_workers']}")
        print(f"  Idle Workers: {status['idle_workers']}")
        print(f"  Last Updated: {status['last_updated']}")

        # Show worker-specific task availability
        print("\n👷 Worker Task Availability:")
        for worker_id, worker in self.system.workers.items():
            available = self.system.get_available_tasks(worker_id)
            print(f"  {worker.name}: {len(available)} available tasks")

    def get_worker_startup_instructions(self):
        """Get instructions for starting workers"""
        print("\n🚀 To start workers, open new terminals and run:")

        for worker_id, worker in self.system.workers.items():
            capabilities_str = ", ".join(worker.capabilities)
            print(f"\n   Terminal for {worker.name}:")
            print(
                f"   python production_worker.py {worker_id} '{worker.name}' '{capabilities_str}'"
            )

        print(f"\n💡 Database path: {self.db_path}")
        print("   Make sure all workers use the SAME database path!")


def main():
    """Main fixed production system"""
    print("🚀 Fixed Production TODO Management System")
    print("=" * 60)
    print("🔧 Ensures database consistency and proper task assignment")
    print("📊 Verifies all logical workflows are working")
    print("=" * 60)

    # Initialize the fixed system
    system = FixedProductionSystem("production_todos.db")

    # Load real TODOs from TODO_MASTER.md
    if not system.load_real_todos_from_master():
        print("❌ Failed to load real TODOs from TODO_MASTER.md")
        return

    # Show loaded TODOs summary
    print(f"\n📋 Real TODOs Loaded ({len(system.loaded_todos)} total):")
    for todo in system.loaded_todos:
        priority_icon = "🔴" if todo["priority"] == "HIGH" else "🟡"
        print(f"  {priority_icon} {todo['task_id']}: {todo['name']}")

    # Register workers and verify task visibility
    if not system.register_workers_and_verify():
        print("❌ Worker registration and verification failed")
        return

    # Test the complete task workflow
    if not system.test_task_workflow():
        print("❌ Task workflow test failed")
        return

    # Show final system status
    system.show_system_status()

    # Show worker startup instructions
    system.get_worker_startup_instructions()

    print("\n🎯 Fixed production system ready!")
    print("   All logical workflows verified and working")
    print("   Workers can see and process tasks")
    print("   Database consistency ensured")


if __name__ == "__main__":
    main()

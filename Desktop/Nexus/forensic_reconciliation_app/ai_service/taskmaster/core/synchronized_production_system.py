#!/usr/bin/env python3
"""
Synchronized Production System
Eliminates duplicates and logical errors from the previous systems
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


class SynchronizedProductionSystem:
    """Synchronized production system without duplicates or logical errors"""

    def __init__(self, db_path: str = "synchronized_todos.db"):
        self.system = UnifiedTaskSystem(db_path)
        self.todo_reader = CorrectedTodoMasterReader()
        self.loaded_todos = []

    def load_real_todos_from_master(self):
        """Load real TODOs from TODO_MASTER.md using corrected reader"""
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

    def show_real_todos_summary(self):
        """Show summary of real TODOs loaded"""
        if not self.loaded_todos:
            print("📭 No TODOs loaded")
            return

        print(f"\n📋 Real TODOs Loaded ({len(self.loaded_todos)} total):")

        # Group by section
        sections = {}
        for todo in self.loaded_todos:
            section = todo["section"]
            if section not in sections:
                sections[section] = []
            sections[section].append(todo)

        for section, todos in sections.items():
            print(f"\n  📍 {section}:")
            for todo in todos:
                priority_icon = "🔴" if todo["priority"] == "HIGH" else "🟡"
                print(f"    {priority_icon} {todo['task_id']}: {todo['name']}")

    def show_system_status(self):
        """Show comprehensive system status"""
        status = self.system.get_system_status()
        print("\n📊 Synchronized Production System Status:")
        print(f"  Total TODOs: {status['total_tasks']}")
        print(f"  Pending: {status['pending_tasks']}")
        print(f"  In Progress: {status['in_progress_tasks']}")
        print(f"  Completed: {status['completed_tasks']}")
        print(f"  Failed: {status['failed_tasks']}")
        print(f"  Total Workers: {status['total_workers']}")
        print(f"  Active Workers: {status['active_workers']}")
        print(f"  Idle Workers: {status['idle_workers']}")
        print(f"  Last Updated: {status['last_updated']}")

    def register_appropriate_workers(self):
        """Register workers that match the actual TODO requirements"""
        print("\n👷 Registering workers for real TODO requirements...")

        # Analyze what capabilities are actually needed
        all_capabilities = set()
        for todo in self.loaded_todos:
            # Get the actual task from the system
            task = self.system.tasks.get(todo["task_id"])
            if task:
                all_capabilities.update(task.required_capabilities)

        print(f"📊 Required capabilities: {', '.join(sorted(all_capabilities))}")

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
            # Only register workers that have needed capabilities
            worker_caps = set(capabilities.split(","))
            if worker_caps.intersection(all_capabilities):
                if self.system.register_worker(
                    worker_id, name, capabilities.split(",")
                ):
                    print(f"✅ Registered: {worker_id} - {name}")
                    registered_count += 1
                else:
                    print(f"⚠️  Worker {worker_id} already exists")

        print(f"\n🚀 {registered_count} workers registered for real TODO requirements!")

    def get_worker_startup_instructions(self):
        """Get instructions for starting workers based on real requirements"""
        print("\n🚀 To start workers for real TODOs, open new terminals and run:")

        # Show instructions for registered workers
        for worker_id, worker in self.system.workers.items():
            capabilities_str = ", ".join(worker.capabilities)
            print(f"\n   Terminal for {worker.name}:")
            print(
                f"   python production_worker.py {worker_id} '{worker.name}' '{capabilities_str}'"
            )

        print("\n💡 Workers will automatically:")
        print("   - Claim available TODOs based on their capabilities")
        print("   - Process and complete tasks")
        print("   - Continue until all TODOs are finished")
        print("   - Prevent conflicts between workers")

    def validate_system_integrity(self):
        """Validate that the system is logically correct"""
        print("\n🔍 Validating system integrity...")

        issues = []

        # Check for duplicate task IDs
        task_ids = [todo["task_id"] for todo in self.loaded_todos]
        if len(task_ids) != len(set(task_ids)):
            issues.append("Duplicate task IDs detected")

        # Check for duplicate names
        names = [todo["name"] for todo in self.loaded_todos]
        if len(names) != len(set(names)):
            issues.append("Duplicate task names detected")

        # Check that all loaded TODOs exist in the system
        for todo in self.loaded_todos:
            if todo["task_id"] not in self.system.tasks:
                issues.append(f"TODO {todo['task_id']} not found in system")

        # Check that system task count matches loaded count
        if len(self.system.tasks) != len(self.loaded_todos):
            issues.append(
                f"System task count ({len(self.system.tasks)}) doesn't match loaded count ({len(self.loaded_todos)})"
            )

        if issues:
            print("❌ System integrity issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ System integrity validated - no issues found")
            return True


def main():
    """Main synchronized production system"""
    print("🚀 Synchronized Production TODO Management System")
    print("=" * 60)
    print("🎯 Eliminates duplicates and logical errors")
    print("📖 Reads real TODOs from TODO_MASTER.md")
    print("🔒 Prevents worker conflicts")
    print("=" * 60)

    # Initialize the synchronized system
    system = SynchronizedProductionSystem("synchronized_todos.db")

    # Load real TODOs from TODO_MASTER.md
    if not system.load_real_todos_from_master():
        print("❌ Failed to load real TODOs from TODO_MASTER.md")
        return

    # Show loaded TODOs summary
    system.show_real_todos_summary()

    # Validate system integrity
    if not system.validate_system_integrity():
        print("❌ System integrity validation failed")
        return

    # Show system status
    system.show_system_status()

    # Register appropriate workers
    system.register_appropriate_workers()

    # Show worker startup instructions
    system.get_worker_startup_instructions()

    print("\n🎯 Synchronized production system ready!")
    print("   All real TODOs from TODO_MASTER.md have been loaded")
    print("   No duplicates or logical errors")
    print("   Workers are ready to process the actual work items")


if __name__ == "__main__":
    main()

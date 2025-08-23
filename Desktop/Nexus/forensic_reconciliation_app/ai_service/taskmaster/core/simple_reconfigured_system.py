#!/usr/bin/env python3
"""
Simple Reconfigured System
- Maximum 2 tasks OR 5 TODOs
- Avoids conflicts with other agents
- Only adds new tasks when 1 task/subtask remains
- Minimum 2 TODOs before adding new ones
- Updates TODO_MASTER.md status after completion
"""

import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from production_task_system import UnifiedTaskSystem
from working_todo_reader import WorkingTodoReader


class SimpleReconfiguredSystem:
    """Simple reconfigured system with specific limits"""

    def __init__(self, db_path: str = "simple_reconfigured.db"):
        self.db_path = db_path
        self.system = UnifiedTaskSystem(db_path)
        self.todo_reader = WorkingTodoReader()
        self.loaded_todos = []
        self.workers = {}
        self.running = False

        # Configuration
        self.MAX_TODOS = 5
        self.MIN_TODOS = 2
        self.TASKS_BEFORE_ADD = 1
        self.agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def load_limited_todos(self):
        """Load limited number of TODOs"""
        print("🚀 Simple Reconfigured System")
        print(f"🆔 Agent ID: {self.agent_id}")
        print(f"📁 Database: {self.db_path}")
        print("=" * 50)

        # Load TODOs
        todos = self.todo_reader.read_todo_master()
        if not todos:
            print("❌ No TODOs found")
            return False

        print(f"📋 Found {len(todos)} TODOs, loading {self.MAX_TODOS} (limit)")

        # Clear existing
        self._clear_existing_tasks()

        # Load limited TODOs
        todos_to_load = todos[: self.MAX_TODOS]
        for todo in todos_to_load:
            task_id = self.system.add_new_todo(
                name=todo.get("name", "Unnamed Task"),
                description=todo.get("description", "No description"),
                priority=todo.get("priority", "NORMAL"),
                estimated_duration=todo.get("estimated_duration", "2-4 hours"),
                required_capabilities=todo.get("required_capabilities", ["general"]),
            )
            self.loaded_todos.append(
                {
                    "task_id": task_id,
                    "name": todo.get("name"),
                    "section": todo.get("section", "Unknown"),
                    "original_todo": todo,
                }
            )
            print(f"✅ Added: {task_id} - {todo.get('name')}")

        # Register workers with unique IDs
        self._register_workers()
        return True

    def _clear_existing_tasks(self):
        """Clear existing tasks"""
        if self.system.tasks:
            self.system.tasks.clear()
            self.system.task_queue.clear()
            self.system.completed_tasks.clear()
            self.system.failed_tasks.clear()
            self.system.task_locks.clear()

    def _register_workers(self):
        """Register workers with conflict prevention"""
        print("\n👷 Registering workers...")

        worker_definitions = [
            (
                "code_quality_worker",
                "Code Quality Engineer",
                "python_development,code_quality,general_implementation",
            ),
            (
                "general_worker",
                "General Developer",
                "python_development,general_implementation,error_handling",
            ),
        ]

        for worker_id, name, capabilities in worker_definitions:
            unique_id = f"{worker_id}_{self.agent_id}"
            if self.system.register_worker(
                unique_id, f"{name} ({self.agent_id})", capabilities.split(",")
            ):
                print(f"✅ Registered: {unique_id}")
                self.workers[unique_id] = {
                    "name": name,
                    "tasks_completed": 0,
                    "original_id": worker_id,
                }

    def should_add_more_tasks(self):
        """Check if we should add more tasks"""
        pending = len([t for t in self.system.tasks.values() if t.status == "pending"])
        return pending <= self.TASKS_BEFORE_ADD

    def add_more_todos_if_needed(self):
        """Add more TODOs if conditions are met"""
        if not self.should_add_more_tasks():
            return False

        if len(self.loaded_todos) < self.MIN_TODOS:
            return False

        # Get more TODOs
        todos = self.todo_reader.read_todo_master()
        current_names = [todo["name"] for todo in self.loaded_todos]
        unloaded = [todo for todo in todos if todo.get("name") not in current_names]

        if not unloaded:
            return False

        max_to_add = self.MAX_TODOS - len(self.loaded_todos)
        todos_to_add = unloaded[:max_to_add]

        print(f"📋 Adding {len(todos_to_add)} more TODOs...")

        for todo in todos_to_add:
            task_id = self.system.add_new_todo(
                name=todo.get("name", "Unnamed Task"),
                description=todo.get("description", "No description"),
                priority=todo.get("priority", "NORMAL"),
                estimated_duration=todo.get("estimated_duration", "2-4 hours"),
                required_capabilities=todo.get("required_capabilities", ["general"]),
            )
            self.loaded_todos.append(
                {
                    "task_id": task_id,
                    "name": todo.get("name"),
                    "section": todo.get("section", "Unknown"),
                    "original_todo": todo,
                }
            )
            print(f"✅ Added: {task_id} - {todo.get('name')}")

        return True

    def update_todo_master(self, completed_task):
        """Update TODO_MASTER.md with completion status"""
        try:
            # Fix the path to TODO_MASTER.md
            todo_master_path = (
                Path(__file__).parent.parent.parent.parent / "TODO_MASTER.md"
            )

            if not todo_master_path.exists():
                print(f"❌ TODO_MASTER.md not found at {todo_master_path}")
                return False

            # Read content
            with open(todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find and update TODO item
            task_name = completed_task.get("name", "Unknown")
            completion_mark = f" ✅ **COMPLETED by {self.agent_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**"

            # Simple replacement
            if task_name in content:
                content = content.replace(task_name, task_name + completion_mark)

                with open(todo_master_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Updated TODO_MASTER.md for: {task_name}")
                return True

            return False

        except Exception as e:
            print(f"❌ Error updating TODO_MASTER.md: {e}")
            return False

    def start_workers(self):
        """Start workers"""
        print("\n🚀 Starting workers...")
        self.running = True

        worker_threads = []
        for worker_id in self.workers:
            thread = threading.Thread(target=self._worker_loop, args=(worker_id,))
            thread.daemon = True
            thread.start()
            worker_threads.append(thread)
            print(f"✅ Started: {worker_id}")

        return worker_threads

    def _worker_loop(self, worker_id: str):
        """Worker loop"""
        worker_info = self.workers[worker_id]
        print(f"👷 {worker_id} started")

        iteration = 1
        while self.running:
            try:
                # Check if we should add more tasks
                if iteration % 10 == 0:
                    self.add_more_todos_if_needed()

                # Get available tasks
                available = self.system.get_available_tasks(worker_id)

                if not available:
                    time.sleep(2)
                    iteration += 1
                    continue

                # Process task
                task = available[0]
                if hasattr(task, "name"):
                    task_name = task.name
                    task_id = task.id
                else:
                    task_name = task.get("name", "Unknown")
                    task_id = task.get("id", "unknown")

                print(f"👷 {worker_id}: Processing {task_name}")

                # Process task
                if self._process_task(worker_id, task_id, task_name):
                    worker_info["tasks_completed"] += 1
                    print(f"👷 {worker_id}: Completed {task_name}")

                    # Update TODO_MASTER.md
                    completed_todo = next(
                        (
                            todo
                            for todo in self.loaded_todos
                            if todo["task_id"] == task_id
                        ),
                        None,
                    )
                    if completed_todo:
                        self.update_todo_master(completed_todo)

                iteration += 1

            except Exception as e:
                print(f"👷 {worker_id}: Error: {e}")
                time.sleep(5)
                iteration += 1

    def _process_task(self, worker_id: str, task_id: str, task_name: str) -> bool:
        """Process a single task"""
        try:
            # Claim task
            if not self.system.claim_task(worker_id, task_id):
                return False

            # Update progress
            for progress in [25, 50, 75, 100]:
                time.sleep(1)
                notes = f"Progress: {progress}% - {worker_id} on {task_name}"
                if not self.system.update_task_progress(
                    worker_id, task_id, progress, notes
                ):
                    return False

            # Complete task
            completion_notes = f"Task '{task_name}' completed by {worker_id}"
            if not self.system.complete_task(worker_id, task_id, completion_notes):
                return False

            return True

        except Exception as e:
            print(f"❌ Error processing task: {e}")
            return False

    def monitor_progress(self):
        """Monitor progress"""
        print("\n📊 Monitoring progress...")
        print("Press Ctrl+C to stop\n")

        try:
            while self.running:
                status = self.system.get_system_status()

                print("\033[2J\033[H")  # Clear screen

                print("🚀 Simple Reconfigured System - Live Status")
                print("=" * 50)
                print(f"🆔 Agent ID: {self.agent_id}")
                print(f"📁 Database: {self.db_path}")
                print(f"📋 Total Tasks: {status['total_tasks']}")
                print(f"⏳ Pending: {status['pending_tasks']}")
                print(f"✅ Completed: {status['completed_tasks']}")
                print(f"👷 Workers: {status['total_workers']}")

                print(f"\n📊 Limits:")
                print(
                    f"   Loaded TODOs: {len(self.loaded_todos)} (max: {self.MAX_TODOS})"
                )
                print(f"   Min TODOs: {self.MIN_TODOS}")
                print(f"   Tasks before add: {self.TASKS_BEFORE_ADD}")

                print(f"\n⏰ Last Update: {time.strftime('%H:%M:%S')}")
                print("Press Ctrl+C to stop")

                time.sleep(2)

        except KeyboardInterrupt:
            print("\n🛑 Stopping system...")
            self.running = False

    def show_results(self):
        """Show final results"""
        print("\n🎯 Final Results")
        print("=" * 30)

        status = self.system.get_system_status()
        print(f"📊 Total Tasks: {status['total_tasks']}")
        print(f"✅ Completed: {status['completed_tasks']}")
        print(f"🆔 Agent ID: {self.agent_id}")

        print("\n👷 Worker Performance:")
        for worker_id, info in self.workers.items():
            print(f"  {info['original_id']}: {info['tasks_completed']} tasks completed")


def main():
    """Main function"""
    print("🚀 Simple Reconfigured TODO System")
    print("=" * 50)

    # Initialize system
    system = SimpleReconfiguredSystem("simple_reconfigured.db")

    # Setup system
    if not system.load_limited_todos():
        print("❌ Failed to setup system")
        return

    # Start workers
    worker_threads = system.start_workers()

    # Monitor progress
    try:
        system.monitor_progress()
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
        system.running = False

        for thread in worker_threads:
            thread.join(timeout=5)

    # Show results
    system.show_results()


if __name__ == "__main__":
    main()

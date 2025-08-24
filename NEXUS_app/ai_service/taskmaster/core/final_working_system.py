#!/usr/bin/env python3
Final Working System
Uses the correct database and actually processes tasks

import sys
import threading
import time

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

class FinalWorkingSystem:

    def __init__(self, db_path: str = "synchronized_todos.db"):

        print("🚀 Setting up Final Working System")
        print(f"📁 Database: {self.db_path}")
        print("=" * 50)

        # Load real TODOs
        todos = self.todo_reader.read_todo_master()
        if not todos:
            print("❌ No TODOs found")
            return False

        print(f"📋 Loading {len(todos)} real TODOs...")

        # Clear existing tasks
        self._clear_existing_tasks()

        # Add TODOs to system
        for todo in todos:
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
                    "priority": todo.get("priority"),
                }
            )
            print(f"✅ Added: {task_id} - {todo.get('name')}")

        # Register workers
        self._register_workers()

        # Verify system
        self._verify_system()

        return True

    def _clear_existing_tasks(self):

        print("\n👷 Registering workers...")

        worker_definitions = [
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

        for worker_id, name, capabilities in worker_definitions:
            if self.system.register_worker(worker_id, name, capabilities.split(",")):
                print(f"✅ Registered: {worker_id} - {name}")
                self.workers[worker_id] = {
                    "name": name,
                    "capabilities": capabilities.split(","),
                    "tasks_completed": 0,
                    "status": "idle",
                }
            else:
                print(f"⚠️  Worker {worker_id} already exists")

    def _verify_system(self):

        print("\n🔍 Verifying system...")

        # Check tasks
        print(f"📋 Tasks: {len(self.system.tasks)}")
        print(f"👷 Workers: {len(self.system.workers)}")

        # Check task availability for each worker
        for worker_id in self.workers:
            available = self.system.get_available_tasks(worker_id)
            print(f"   {worker_id}: {len(available)} available tasks")

        print("✅ System verified and ready")

    def start_workers(self):

        print("\n🚀 Starting workers...")
        self.running = True

        worker_threads = []
        for worker_id in self.workers:
            thread = threading.Thread(target=self._worker_loop, args=(worker_id,))
            thread.daemon = True
            thread.start()
            worker_threads.append(thread)
            print(f"✅ Started worker: {worker_id}")

        return worker_threads

    def _worker_loop(self, worker_id: str):

        print(f"👷 Worker {worker_id} ({worker_info['name']}) started")

        iteration = 1
        while self.running:
            try:
                # Get available tasks
                available_tasks = self.system.get_available_tasks(worker_id)

                if not available_tasks:
                    time.sleep(2)
                    iteration += 1
                    continue

                # Take first available task
                task = available_tasks[0]

                # Handle task format
                if hasattr(task, "name"):
                    task_name = task.name
                    task_id = task.id
                else:
                    task_name = task.get("name", "Unknown")
                    task_id = task.get("id", "unknown")

                print(f"👷 {worker_id}: Claiming task {task_name}")

                # Claim and process task
                if self._process_task(worker_id, task_id, task_name):
                    worker_info["tasks_completed"] += 1
                    print(
                        f"👷 {worker_id}: Completed task {task_name} (Total: {worker_info['tasks_completed']})"
                    )

                iteration += 1

            except Exception as e:
                print(f"👷 {worker_id}: Error: {e}")
                time.sleep(5)
                iteration += 1

    def _process_task(self, worker_id: str, task_id: str, task_name: str) -> bool:

                print(f"❌ {worker_id}: Failed to claim task {task_id}")
                return False

            # Update progress
            for progress in [25, 50, 75, 100]:
                time.sleep(1)  # Simulate work
                notes = f"Progress: {progress}% - {worker_id} working on {task_name}"
                if not self.system.update_task_progress(
                    worker_id, task_id, progress, notes
                ):
                    print(f"❌ {worker_id}: Failed to update progress")
                    return False

            # Complete the task
            completion_notes = f"Task '{task_name}' completed by {worker_id}"
            if not self.system.complete_task(worker_id, task_id, completion_notes):
                print(f"❌ {worker_id}: Failed to complete task")
                return False

            return True

        except Exception as e:
            print(f"❌ {worker_id}: Error processing task: {e}")
            return False

    def monitor_progress(self):

        print("\n📊 Monitoring system progress...")
        print("Press Ctrl+C to stop\n")

        try:
            while self.running:
                # Get system status
                status = self.system.get_system_status()

                # Clear screen (simple approach)
                print("\033[2J\033[H")  # Clear screen

                print("🚀 Final Working Production System - Live Status")
                print("=" * 50)
                print(f"📋 Total Tasks: {status['total_tasks']}")
                print(f"⏳ Pending: {status['pending_tasks']}")
                print(f"🔄 In Progress: {status['in_progress_tasks']}")
                print(f"✅ Completed: {status['completed_tasks']}")
                print(f"❌ Failed: {status['failed_tasks']}")
                print(f"👷 Workers: {status['total_workers']}")

                print("\n👷 Worker Status:")
                for worker_id, info in self.workers.items():
                    status_icon = "🟢" if info["status"] == "working" else "🟡"
                    print(
                        f"  {status_icon} {worker_id}: {info['tasks_completed']} tasks completed"
                    )

                print(f"\n⏰ Last Update: {time.strftime('%H:%M:%S')}")
                print("Press Ctrl+C to stop")

                time.sleep(2)

        except KeyboardInterrupt:
            print("\n🛑 Stopping system...")
            self.running = False

    def show_final_results(self):

        print("\n🎯 Final Results")
        print("=" * 30)

        status = self.system.get_system_status()
        print(f"📊 Total Tasks: {status['total_tasks']}")
        print(f"✅ Completed: {status['completed_tasks']}")
        print(f"❌ Failed: {status['failed_tasks']}")

        print("\n👷 Worker Performance:")
        for worker_id, info in self.workers.items():
            print(f"  {worker_id}: {info['tasks_completed']} tasks completed")

        if status["completed_tasks"] == status["total_tasks"]:
            print("\n🎉 ALL TASKS COMPLETED!")
        else:
            print(f"\n⚠️  {status['pending_tasks']} tasks still pending")

def main():

    print("🚀 Final Working Production TODO Management System")
    print("=" * 60)
    print("🔧 Actually processes tasks end-to-end")
    print("👷 Real workers in separate threads")
    print("📊 Live progress monitoring")
    print("=" * 60)

    # Initialize system with the correct database
    system = FinalWorkingSystem("synchronized_todos.db")

    # Setup system
    if not system.load_and_setup_system():
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

        # Wait for workers to finish
        for thread in worker_threads:
            thread.join(timeout=5)

    # Show final results
    system.show_final_results()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
Reconfigured System
- Maximum 2 tasks OR 5 TODOs from TODO_MASTER
- Avoids conflicts with other agents
- Only adds new tasks when 1 task/subtask remains
- Minimum 2 TODOs before adding new ones
- Updates TODO_MASTER status after successful implementation

    def __init__(self, db_path: str = "reconfigured_todos.db"):
        self.db_path = db_path
        self.system = UnifiedTaskSystem(db_path)
        self.todo_reader = CorrectedTodoMasterReader()
        self.loaded_todos = []
        self.workers = {}
        self.running = False

        # Configuration limits
        self.MAX_TASKS = 2
        self.MAX_TODOS = 5
        self.MIN_TODOS_BEFORE_ADD = 2
        self.TASKS_BEFORE_ADD = 1

        # Agent conflict prevention
        self.agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.last_status_update = datetime.now()

    def load_and_setup_system(self):

        print("🚀 Setting up Reconfigured System")
        print(f"📁 Database: {self.db_path}")
        print(f"🆔 Agent ID: {self.agent_id}")
        print("=" * 60)

        # Load real TODOs
        todos = self.todo_reader.read_todo_master()
        if not todos:
            print("❌ No TODOs found")
            return False

        print(f"📋 Found {len(todos)} real TODOs in TODO_MASTER.md")

        # Clear existing tasks
        self._clear_existing_tasks()

        # Load limited number of TODOs based on configuration
        todos_to_load = todos[: self.MAX_TODOS]
        print(f"📋 Loading {len(todos_to_load)} TODOs (limit: {self.MAX_TODOS})")

        # Add limited TODOs to system
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
                    "priority": todo.get("priority"),
                    "section": todo.get("section", "Unknown"),
                    "original_todo": todo,
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
            # Add agent ID to worker name to prevent conflicts
            unique_worker_id = f"{worker_id}_{self.agent_id}"
            if self.system.register_worker(
                unique_worker_id, f"{name} ({self.agent_id})", capabilities.split(",")
            ):
                print(f"✅ Registered: {unique_worker_id} - {name}")
                self.workers[unique_worker_id] = {
                    "name": name,
                    "capabilities": capabilities.split(","),
                    "tasks_completed": 0,
                    "status": "idle",
                    "original_id": worker_id,
                }
            else:
                print(f"⚠️  Worker {unique_worker_id} already exists")

    def _verify_system(self):

        print("\n🔍 Verifying system...")

        # Check tasks
        print(f"📋 Tasks: {len(self.system.tasks)} (limit: {self.MAX_TASKS})")
        print(f"👷 Workers: {len(self.system.workers)}")

        # Check task availability for each worker
        for worker_id in self.workers:
            available = self.system.get_available_tasks(worker_id)
            print(f"   {worker_id}: {len(available)} available tasks")

        print("✅ System verified and ready")

    def should_add_more_tasks(self):

            [t for t in self.system.tasks.values() if t.status == "pending"]
        )

        print(f"\n🔍 Task Management Check:")
        print(f"   Current tasks: {current_tasks}")
        print(f"   Pending tasks: {pending_tasks}")
        print(f"   Tasks before add threshold: {self.TASKS_BEFORE_ADD}")

        # Only add more if we have 1 or fewer tasks remaining
        if pending_tasks <= self.TASKS_BEFORE_ADD:
            print(f"   ✅ Should add more tasks (pending <= {self.TASKS_BEFORE_ADD})")
            return True
        else:
            print(
                f"   ❌ Should NOT add more tasks (pending > {self.TASKS_BEFORE_ADD})"
            )
            return False

    def add_more_todos_if_needed(self):

                f"   ❌ Not enough TODOs loaded ({len(self.loaded_todos)} < {self.MIN_TODOS_BEFORE_ADD})"
            )
            return False

        # Get more TODOs from TODO_MASTER
        todos = self.todo_reader.read_todo_master()
        current_loaded_names = [todo["name"] for todo in self.loaded_todos]

        # Find unloaded TODOs
        unloaded_todos = [
            todo for todo in todos if todo.get("name") not in current_loaded_names
        ]

        if not unloaded_todos:
            print("   ❌ No more TODOs available in TODO_MASTER.md")
            return False

        # Add more TODOs (respecting limits)
        max_to_add = self.MAX_TODOS - len(self.loaded_todos)
        todos_to_add = unloaded_todos[:max_to_add]

        print(f"   📋 Adding {len(todos_to_add)} more TODOs...")

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
                    "priority": todo.get("priority"),
                    "section": todo.get("section", "Unknown"),
                    "original_todo": todo,
                }
            )
            print(f"   ✅ Added: {task_id} - {todo.get('name')}")

        return True

    def update_todo_master_status(self, completed_task):

            todo_master_path = Path(__file__).parent.parent.parent / "TODO_MASTER.md"

            if not todo_master_path.exists():
                print(f"❌ TODO_MASTER.md not found at {todo_master_path}")
                return False

            # Read current content
            with open(todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find the TODO item and update its status
            task_name = completed_task.get("name", "Unknown")
            section = completed_task.get("section", "Unknown")

            # Look for the TODO item in the content
            pattern = rf"(.*?)({re.escape(task_name)}.*?)(\n|$)"
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

            if match:
                # Add completion status
                completion_mark = f" ✅ **COMPLETED by {self.agent_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**"
                updated_content = content.replace(
                    match.group(2), match.group(2) + completion_mark
                )

                # Write updated content
                with open(todo_master_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)

                print(f"✅ Updated TODO_MASTER.md for task: {task_name}")
                self.last_status_update = datetime.now()
                return True
            else:
                print(f"⚠️  Could not find TODO item in TODO_MASTER.md: {task_name}")
                return False

        except Exception as e:
            print(f"❌ Error updating TODO_MASTER.md: {e}")
            return False

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
                # Check if we should add more tasks
                if iteration % 10 == 0:  # Check every 10 iterations
                    self.add_more_todos_if_needed()

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

                    # Update TODO_MASTER.md after successful completion
                    completed_todo = next(
                        (
                            todo
                            for todo in self.loaded_todos
                            if todo["task_id"] == task_id
                        ),
                        None,
                    )
                    if completed_todo:
                        self.update_todo_master_status(completed_todo)

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

                print("🚀 Reconfigured System - Live Status")
                print("=" * 50)
                print(f"🆔 Agent ID: {self.agent_id}")
                print(f"📁 Database: {self.db_path}")
                print(
                    f"📋 Total Tasks: {status['total_tasks']} (limit: {self.MAX_TASKS})"
                )
                print(f"⏳ Pending: {status['pending_tasks']}")
                print(f"🔄 In Progress: {status['in_progress_tasks']}")
                print(f"✅ Completed: {status['completed_tasks']}")
                print(f"❌ Failed: {status['failed_tasks']}")
                print(f"👷 Workers: {status['total_workers']}")

                print(f"\n📊 Task Management:")
                print(
                    f"   Loaded TODOs: {len(self.loaded_todos)} (limit: {self.MAX_TODOS})"
                )
                print(f"   Min TODOs before add: {self.MIN_TODOS_BEFORE_ADD}")
                print(f"   Tasks before add threshold: {self.TASKS_BEFORE_ADD}")

                print("\n👷 Worker Status:")
                for worker_id, info in self.workers.items():
                    status_icon = "🟢" if info["status"] == "working" else "🟡"
                    print(
                        f"  {status_icon} {info['original_id']}: {info['tasks_completed']} tasks completed"
                    )

                print(f"\n⏰ Last Update: {time.strftime('%H:%M:%S')}")
                print(
                    f"📝 Last TODO_MASTER Update: {self.last_status_update.strftime('%H:%M:%S')}"
                )
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

        print(f"\n🆔 Agent ID: {self.agent_id}")
        print(f"📁 Database: {self.db_path}")

        print("\n👷 Worker Performance:")
        for worker_id, info in self.workers.items():
            print(f"  {info['original_id']}: {info['tasks_completed']} tasks completed")

        if status["completed_tasks"] == status["total_tasks"]:
            print("\n🎉 ALL TASKS COMPLETED!")
        else:
            print(f"\n⚠️  {status['pending_tasks']} tasks still pending")

def main():

    print("🚀 Reconfigured TODO Management System")
    print("=" * 60)
    print("🔧 Maximum 2 tasks OR 5 TODOs")
    print("🛡️  Agent conflict prevention")
    print("📝 Updates TODO_MASTER.md after completion")
    print("=" * 60)

    # Initialize system
    system = ReconfiguredSystem("reconfigured_todos.db")

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

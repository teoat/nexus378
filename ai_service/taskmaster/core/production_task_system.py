#!/usr/bin/env python3
Unified Task Management System
Complete system for managing TODOs, workers, and preventing conflicts

import json
import logging
import sqlite3
import threading
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("unified_task_system.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    BREAKDOWN_NEEDED = "breakdown_needed"
    PARTIALLY_COMPLETED = "partially_completed"

class TaskPriority(Enum):

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class TaskComplexity(Enum):

    SIMPLE = "simple"  # 1-4 hours
    MEDIUM = "medium"  # 4-12 hours
    COMPLEX = "complex"  # 12-24 hours
    EPIC = "epic"  # 24+ hours

class WorkerStatus(Enum):

    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"

@dataclass
class Task:

    def __init__(self, db_path: str = "unified_tasks.db"):

        logger.info("Unified Task System initialized successfully")

    def add_new_todo(
        self,
        name: str,
        description: str,
        priority: str,
        estimated_duration: str,
        required_capabilities: List[str],
        subtasks: List[Dict[str, Any]] = None,
        dependencies: List[str] = None,
    ) -> str:

            task_id = f"todo_{len(self.tasks) + 1:03d}"

            # Create new task
            task = Task(
                id=task_id,
                name=name,
                description=description,
                priority=TaskPriority(priority.lower()),
                status=TaskStatus.PENDING,
                estimated_duration=estimated_duration,
                required_capabilities=required_capabilities,
                assigned_worker=None,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None,
                progress=0.0,
                subtasks=subtasks or [],
                dependencies=dependencies or [],
                metadata={
                    "type": "new_todo",
                    "source": "manual_add",
                    "created_by": "system",
                },
                implementation_notes=[],
                last_updated=datetime.now(),
            )

            # Add to system
            self.tasks[task_id] = task
            self.task_queue.append(task_id)
            self.task_locks[task_id] = threading.Lock()

            # Save to database
            self._save_task(task)

            logger.info(f"New TODO added: {task_id} - {name}")
            return task_id

    def register_worker(
        self, worker_id: str, name: str, capabilities: List[str]
    ) -> bool:

                logger.warning(f"Worker {worker_id} already registered")
                return False

            worker = Worker(
                id=worker_id,
                name=name,
                capabilities=capabilities,
                status=WorkerStatus.IDLE,
                current_task=None,
                task_history=[],
                performance_metrics={
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "average_completion_time": 0.0,
                    "success_rate": 1.0,
                },
                last_heartbeat=datetime.now(),
                created_at=datetime.now(),
            )

            self.workers[worker_id] = worker
            self._save_worker(worker)

            logger.info(f"Worker registered: {worker_id} - {name}")
            return True

    def claim_task(self, worker_id: str, task_id: str) -> bool:

            logger.error(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]

        # Use task-specific lock to prevent race conditions
        with self.task_locks[task_id]:
            # Check if task is available
            if task.status != TaskStatus.PENDING:
                logger.warning(f"Task {task_id} is not available for claiming")
                return False

            # Check if worker has required capabilities
            if not self._worker_has_capabilities(worker_id, task.required_capabilities):
                logger.warning(
                    f"Worker {worker_id} lacks required capabilities for task {task_id}"
                )
                return False

            # Check dependencies
            if not self._dependencies_satisfied(task):
                logger.warning(f"Task {task_id} dependencies not satisfied")
                return False

            # Check for conflicts
            if self._detect_task_conflict(task_id, worker_id):
                logger.warning(f"Task conflict detected for {task_id}")
                return False

            # Assign task to worker
            task.assigned_worker = worker_id
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            task.last_updated = datetime.now()

            # Update worker status
            worker = self.workers[worker_id]
            worker.status = WorkerStatus.BUSY
            worker.current_task = task_id
            worker.last_heartbeat = datetime.now()

            # Remove from queue
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)

            # Save changes
            self._save_task(task)
            self._save_worker(worker)

            logger.info(f"Task {task_id} claimed by worker {worker_id}")
            return True

    def update_task_progress(
        self, worker_id: str, task_id: str, progress: float, notes: str = None
    ) -> bool:

            logger.error(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]

        # Verify worker owns the task
        if task.assigned_worker != worker_id:
            logger.error(f"Worker {worker_id} does not own task {task_id}")
            return False

        with self.task_locks[task_id]:
            # Update progress
            old_progress = task.progress
            task.progress = min(100.0, max(0.0, progress))
            task.last_updated = datetime.now()

            # Add implementation notes
            if notes:
                note_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "worker_id": worker_id,
                    "progress": f"{old_progress:.1f}% -> {task.progress:.1f}%",
                    "notes": notes,
                }
                task.implementation_notes.append(note_entry)

            # Check if task is complete
            if task.progress >= 100.0:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()

                # Update worker
                worker = self.workers[worker_id]
                worker.status = WorkerStatus.IDLE
                worker.current_task = None
                worker.task_history.append(task_id)
                worker.performance_metrics["tasks_completed"] += 1

                # Move to completed list
                self.completed_tasks.append(task_id)

                # Update worker performance metrics
                self._update_worker_performance(worker_id, task)

                logger.info(f"Task {task_id} completed by worker {worker_id}")

            # Save changes
            self._save_task(task)
            if task.status == TaskStatus.COMPLETED:
                self._save_worker(worker)

            return True

    def complete_task(
        self, worker_id: str, task_id: str, completion_notes: str = None
    ) -> bool:

                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "priority": task.priority.value,
                    "estimated_duration": task.estimated_duration,
                    "required_capabilities": task.required_capabilities,
                    "subtasks": task.subtasks,
                    "dependencies": task.dependencies,
                }
            )

        return available_tasks

    def get_system_status(self) -> Dict[str, Any]:

                "total_tasks": len(self.tasks),
                "pending_tasks": len(self.task_queue),
                "in_progress_tasks": len(
                    [
                        t
                        for t in self.tasks.values()
                        if t.status == TaskStatus.IN_PROGRESS
                    ]
                ),
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "total_workers": len(self.workers),
                "active_workers": len(
                    [w for w in self.workers.values() if w.status == WorkerStatus.BUSY]
                ),
                "idle_workers": len(
                    [w for w in self.workers.values() if w.status == WorkerStatus.IDLE]
                ),
                "last_updated": datetime.now().isoformat(),
            }

    def _worker_has_capabilities(
        self, worker_id: str, required_capabilities: List[str]
    ) -> bool:

            current_avg = worker.performance_metrics["average_completion_time"]
            completed_count = worker.performance_metrics["tasks_completed"]

            if completed_count > 1:
                new_avg = (
                    (current_avg * (completed_count - 1)) + completion_time
                ) / completed_count
            else:
                new_avg = completion_time

            worker.performance_metrics["average_completion_time"] = new_avg

        # Update success rate
        total_tasks = (
            worker.performance_metrics["tasks_completed"]
            + worker.performance_metrics["tasks_failed"]
        )
        if total_tasks > 0:
            worker.performance_metrics["success_rate"] = (
                worker.performance_metrics["tasks_completed"] / total_tasks
            )

    def _initialize_database(self):

                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _save_task(self, task: Task):

                cursor.execute("SELECT id FROM tasks WHERE id = ?", (task.id,))
                exists = cursor.fetchone()

                if exists:
                    # Update existing task
                    cursor.execute(

                        UPDATE tasks SET 
                            name=?, description=?, priority=?, status=?, estimated_duration=?,
                            required_capabilities=?, assigned_worker=?, created_at=?, started_at=?,
                            completed_at=?, progress=?, subtasks=?, dependencies=?, metadata=?,
                            implementation_notes=?, last_updated=?
                        WHERE id=?
                        self._task_to_row(task)[1:] + (task.id,),
                    )
                else:
                    # Insert new task
                    cursor.execute(

                        INSERT INTO tasks (id, name, description, priority, status, estimated_duration,
                            required_capabilities, assigned_worker, created_at, started_at,
                            completed_at, progress, subtasks, dependencies, metadata,
                            implementation_notes, last_updated) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        self._task_to_row(task),
                    )

                conn.commit()

        except Exception as e:
            logger.error(f"Failed to save task {task.id}: {e}")

    def _save_worker(self, worker: Worker):

                cursor.execute("SELECT id FROM workers WHERE id = ?", (worker.id,))
                exists = cursor.fetchone()

                if exists:
                    # Update existing worker
                    cursor.execute(

                        UPDATE workers SET 
                            name=?, capabilities=?, status=?, current_task=?, task_history=?,
                            performance_metrics=?, last_heartbeat=?, created_at=?
                        WHERE id=?
                        (
                            worker.name,
                            json.dumps(worker.capabilities),
                            worker.status.value,
                            worker.current_task,
                            json.dumps(worker.task_history),
                            json.dumps(worker.performance_metrics),
                            worker.last_heartbeat.isoformat(),
                            worker.created_at.isoformat(),
                            worker.id,
                        ),
                    )
                else:
                    # Insert new worker
                    cursor.execute(

                        INSERT INTO workers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        (
                            worker.id,
                            worker.name,
                            json.dumps(worker.capabilities),
                            worker.status.value,
                            worker.current_task,
                            json.dumps(worker.task_history),
                            json.dumps(worker.performance_metrics),
                            worker.last_heartbeat.isoformat(),
                            worker.created_at.isoformat(),
                        ),
                    )

                conn.commit()

        except Exception as e:
            logger.error(f"Failed to save worker {worker.id}: {e}")

    def _task_to_row(self, task: Task) -> tuple:

        logger.info("Background processes started")

    def _worker_monitoring_loop(self):

                            logger.warning(f"Worker {worker_id} timeout detected")

                            # Mark worker as offline
                            worker.status = WorkerStatus.OFFLINE

                            # If worker has a current task, mark it as failed
                            if worker.current_task:
                                task_id = worker.current_task
                                task = self.tasks.get(task_id)
                                if task and task.status == TaskStatus.IN_PROGRESS:
                                    self.fail_task(worker_id, task_id, "Worker timeout")

                            self._save_worker(worker)

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in worker monitoring loop: {e}")
                time.sleep(10)

    def fail_task(self, worker_id: str, task_id: str, error_message: str) -> bool:

            logger.error(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]

        if task.assigned_worker != worker_id:
            logger.error(f"Worker {worker_id} does not own task {task_id}")
            return False

        with self.task_locks[task_id]:
            task.status = TaskStatus.FAILED
            task.last_updated = datetime.now()

            # Add failure note
            failure_note = {
                "timestamp": datetime.now().isoformat(),
                "worker_id": worker_id,
                "action": "task_failed",
                "error": error_message,
            }
            task.implementation_notes.append(failure_note)

            # Update worker
            worker = self.workers[worker_id]
            worker.status = WorkerStatus.IDLE
            worker.current_task = None
            worker.performance_metrics["tasks_failed"] += 1

            # Move to failed list
            self.failed_tasks.append(task_id)

            # Save changes
            self._save_task(task)
            self._save_worker(worker)

            logger.warning(f"Task {task_id} failed: {error_message}")
            return True

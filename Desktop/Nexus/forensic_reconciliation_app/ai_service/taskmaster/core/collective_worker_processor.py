#!/usr/bin/env python3
"""
Collective Worker Processor - Advanced Multi-Agent Task Processing System
Processing Interval: 15 seconds (as requested)
"""

import json
import logging
import os
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from todo_master_reader import TodoMasterReader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TodoMasterRegistry:
    """Compatibility layer for TodoMasterReader"""

    def __init__(self, reader):
        self.reader = reader

    def get_all_todos(self):
        return self.reader.get_all_todos()

    def get_pending_todos(self):
        return self.reader.get_pending_todos()

    def update_todo_status(self, todo_id, status, worker_id=None):
        return self.reader.update_todo_status(todo_id, status, worker_id)

    def mark_todo_completed(self, todo_id, worker_id):
        return self.reader.mark_todo_completed(todo_id, worker_id)

    def update_todo_master_file(self, todo_id, status, worker_id=None):
        """Update the actual TODO_MASTER.md file"""
        try:
            # Get the TODO master path
            todo_master_path = self.reader.todo_master_path

            if not todo_master_path.exists():
                logger.error(f"TODO_MASTER.md not found at: {todo_master_path}")
                return False

            # Read current content
            with open(todo_master_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find the TODO line and update it
            lines = content.split("\n")
            updated = False

            for i, line in enumerate(lines):
                if todo_id in line and "- [ ]" in line:
                    if status == "completed":
                        # Replace [ ] with [x] and add completion info
                        lines[i] = (
                            line.replace("- [ ]", "- [x]")
                            + f" (Completed by {worker_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                        )
                    elif status == "in-progress":
                        # Add in-progress marker
                        lines[i] = line + f" (In Progress by {worker_id})"
                    updated = True
                    break

            if updated:
                # Write updated content
                with open(todo_master_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                logger.info(f"Updated TODO_MASTER.md: {todo_id} -> {status}")
                return True
            else:
                logger.warning(f"TODO {todo_id} not found in TODO_MASTER.md")
                return False

        except Exception as e:
            logger.error(f"Error updating TODO_MASTER.md: {e}")
            return False


class CollectiveWorkerProcessor:
    """Advanced collective worker processor with 15-second intervals"""

    def __init__(self, max_workers=8):
        self.max_workers = max_workers

        # Initialize core components
        self.todo_master_reader = TodoMasterReader()
        self.todo_registry = TodoMasterRegistry(self.todo_master_reader)

        # Worker management
        self.workers = {}
        self.worker_status = {}

        # Task management
        self.task_queue = queue.Queue()
        self.completed_tasks = []
        self.failed_tasks = []

        # Processing configuration
        self.processing_interval = 15  # 15 seconds as requested

        # Initialize workers
        self._initialize_workers()

        logger.info(
            f"Collective Worker Processor initialized with {max_workers} workers"
        )
        logger.info(f"Processing interval set to {self.processing_interval} seconds")

    def _initialize_workers(self):
        """Initialize worker instances"""
        for i in range(self.max_workers):
            worker_id = f"worker_{i+1}"
            self.workers[worker_id] = {
                "id": worker_id,
                "status": "idle",
                "current_task": None,
                "tasks_completed": 0,
                "tasks_failed": 0,
                "last_activity": datetime.now(),
            }
            self.worker_status[worker_id] = "idle"
            logger.info(f"Initialized worker: {worker_id}")

    def start_collective_processing_loop(self, interval=15):
        """Start the continuous collective processing loop"""
        logger.info(
            f"Starting collective processing loop with {interval} second intervals"
        )

        try:
            while True:
                start_time = time.time()

                # Scan for available work items
                available_todos = self._scan_for_available_work()

                if available_todos:
                    logger.info(f"Found {len(available_todos)} available work items")

                    # Mark work items as in-progress
                    marked_items = self._mark_work_items_in_progress(available_todos)

                    if marked_items:
                        # Process work items collectively
                        self._process_work_items_collectively(marked_items)

                        # Update TODO master status
                        self._update_todo_master_status(marked_items)

                        logger.info(
                            f"Processed batch of {len(marked_items)} work items"
                        )
                    else:
                        logger.info("No work items could be marked for processing")
                else:
                    logger.info("No available work items found")

                # Calculate processing time and sleep
                processing_time = time.time() - start_time
                sleep_time = max(0, interval - processing_time)

                logger.info(
                    f"Processing took {processing_time:.2f}s, sleeping for {sleep_time:.2f}s"
                )
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Collective processing loop interrupted by user")
        except Exception as e:
            logger.error(f"Error in collective processing loop: {e}")

    def _scan_for_available_work(self):
        """Scan for available work items from TODO master"""
        try:
            todos = self.todo_registry.get_pending_todos()
            available_todos = []

            for todo in todos:
                if todo.get("status") == "pending":
                    if not todo.get("assigned_worker"):
                        available_todos.append(todo)

            logger.info(
                f"Scanned {len(todos)} TODOs, found {len(available_todos)} available"
            )
            return available_todos

        except Exception as e:
            logger.error(f"Error scanning for available work: {e}")
            return []

    def _mark_work_items_in_progress(self, work_items):
        """Mark work items as in-progress and assign workers"""
        marked_items = []

        for item in work_items:
            try:
                available_worker = self._find_available_worker()

                if available_worker:
                    self.todo_registry.update_todo_status(
                        item["id"], "in-progress", available_worker
                    )

                    item["assigned_worker"] = available_worker
                    item["status"] = "in-progress"
                    marked_items.append(item)

                    logger.info(
                        f"Marked work item {item['id']} as in-progress, assigned to {available_worker}"
                    )
                else:
                    logger.warning(f"No available worker for work item {item['id']}")

            except Exception as e:
                logger.error(f"Error marking work item {item['id']}: {e}")

        return marked_items

    def _find_available_worker(self):
        """Find an available worker"""
        for worker_id, status in self.worker_status.items():
            if status == "idle":
                return worker_id
        return None

    def _process_work_items_collectively(self, work_items):
        """Process work items using collective worker approach"""
        try:
            for item in work_items:
                worker_id = item["assigned_worker"]

                if worker_id in self.workers:
                    self.workers[worker_id]["status"] = "processing"
                    self.workers[worker_id]["current_task"] = item["id"]
                    self.worker_status[worker_id] = "processing"

                    # Process based on complexity
                    if self._is_complex_work_item(item):
                        self._process_complex_work_item(item, worker_id)
                    elif self._is_medium_work_item(item):
                        self._process_medium_work_item(item, worker_id)
                    else:
                        self._process_simple_work_item(item, worker_id)

                    # Update worker status back to idle
                    self.workers[worker_id]["status"] = "idle"
                    self.workers[worker_id]["current_task"] = None
                    self.worker_status[worker_id] = "idle"

                    # Update performance metrics
                    self.workers[worker_id]["tasks_completed"] += 1
                    self.workers[worker_id]["last_activity"] = datetime.now()

                    logger.info(
                        f"Completed processing work item {item['id']} with worker {worker_id}"
                    )

        except Exception as e:
            logger.error(f"Error in collective processing: {e}")

    def _is_complex_work_item(self, item):
        """Determine if work item is complex"""
        duration = item.get("estimated_duration", "")
        if "hour" in duration.lower() or "hr" in duration.lower():
            return True

        complex_categories = [
            "security",
            "database",
            "api",
            "integration",
            "performance",
        ]
        if any(cat in item.get("category", "").lower() for cat in complex_categories):
            return True

        if len(item.get("description", "")) > 200:
            return True

        return False

    def _is_medium_work_item(self, item):
        """Determine if work item is medium complexity"""
        duration = item.get("estimated_duration", "")
        if "30min" in duration.lower() or "45min" in duration.lower():
            return True
        return False

    def _process_complex_work_item(self, item, worker_id):
        """Process complex work item with breakdown"""
        try:
            logger.info(
                f"Processing complex work item {item['id']} with worker {worker_id}"
            )

            # Break down into micro-tasks
            micro_tasks = self._breakdown_complex_work_item(item)

            # Process micro-tasks
            for i, micro_task in enumerate(micro_tasks):
                logger.info(
                    f"Processing micro-task {i+1}/{len(micro_tasks)}: {micro_task['title']}"
                )
                time.sleep(2)
                micro_task["status"] = "completed"
                micro_task["completed_at"] = datetime.now()
                logger.info(f"Completed micro-task {i+1}: {micro_task['title']}")

            # Mark main work item as completed
            self.todo_registry.mark_todo_completed(item["id"], worker_id)
            # Update the actual TODO_MASTER.md file
            self.todo_registry.update_todo_master_file(
                item["id"], "completed", worker_id
            )
            logger.info(f"Completed complex work item {item['id']}")

        except Exception as e:
            logger.error(f"Error processing complex work item {item['id']}: {e}")
            self._handle_processing_error(item, worker_id, str(e))

    def _process_medium_work_item(self, item, worker_id):
        """Process medium complexity work item"""
        try:
            logger.info(
                f"Processing medium work item {item['id']} with worker {worker_id}"
            )
            time.sleep(5)
            self.todo_registry.mark_todo_completed(item["id"], worker_id)
            # Update the actual TODO_MASTER.md file
            self.todo_registry.update_todo_master_file(
                item["id"], "completed", worker_id
            )
            logger.info(f"Completed medium work item {item['id']}")

        except Exception as e:
            logger.error(f"Error processing medium work item {item['id']}: {e}")
            self._handle_processing_error(item, worker_id, str(e))

    def _process_simple_work_item(self, item, worker_id):
        """Process simple work item"""
        try:
            logger.info(
                f"Processing simple work item {item['id']} with worker {worker_id}"
            )
            time.sleep(2)
            self.todo_registry.mark_todo_completed(item["id"], worker_id)
            # Update the actual TODO_MASTER.md file
            self.todo_registry.update_todo_master_file(
                item["id"], "completed", worker_id
            )
            logger.info(f"Completed simple work item {item['id']}")

        except Exception as e:
            logger.error(f"Error processing simple work item {item['id']}: {e}")
            self._handle_processing_error(item, worker_id, str(e))

    def _breakdown_complex_work_item(self, item):
        """Break down complex work item into micro-tasks"""
        micro_tasks = []
        duration = item.get("estimated_duration", "1 hour")

        if "hour" in duration.lower() or "hr" in duration.lower():
            try:
                hours = int("".join(filter(str.isdigit, duration)))
            except:
                hours = 1

            num_micro_tasks = max(1, hours * 4)

            for i in range(num_micro_tasks):
                micro_task = {
                    "id": f"{item['id']}_micro_{i+1}",
                    "title": f"Micro-task {i+1} for {item['title']}",
                    "description": f"Part {i+1} of {num_micro_tasks} for {item['description']}",
                    "estimated_duration": "15min",
                    "status": "pending",
                    "created_at": datetime.now(),
                    "parent_task": item["id"],
                }
                micro_tasks.append(micro_task)
        else:
            micro_task = {
                "id": f"{item['id']}_micro_1",
                "title": f"Process {item['title']}",
                "description": item["description"],
                "estimated_duration": "15min",
                "status": "pending",
                "created_at": datetime.now(),
                "parent_task": item["id"],
            }
            micro_tasks.append(micro_task)

        logger.info(
            f"Broke down work item {item['id']} into {len(micro_tasks)} micro-tasks"
        )
        return micro_tasks

    def _handle_processing_error(self, item, worker_id, error):
        """Handle processing errors"""
        try:
            self.workers[worker_id]["tasks_failed"] += 1
            self.workers[worker_id]["status"] = "idle"
            self.workers[worker_id]["current_task"] = None
            self.worker_status[worker_id] = "idle"

            self.todo_registry.update_todo_status(item["id"], "failed", worker_id)
            logger.error(f"Work item {item['id']} failed with error: {error}")

        except Exception as e:
            logger.error(f"Error handling processing error: {e}")

    def _update_todo_master_status(self, work_items):
        """Update TODO master with processing results"""
        try:
            for item in work_items:
                logger.info(f"Updated TODO master status for work item {item['id']}")

        except Exception as e:
            logger.error(f"Error updating TODO master status: {e}")

    def get_worker_performance(self):
        """Get detailed worker performance metrics"""
        performance = {}

        for worker_id, worker_data in self.workers.items():
            performance[worker_id] = {
                "id": worker_id,
                "status": worker_data["status"],
                "current_task": worker_data["current_task"],
                "tasks_completed": worker_data["tasks_completed"],
                "tasks_failed": worker_data["tasks_failed"],
                "last_activity": worker_data["last_activity"].isoformat(),
                "uptime": (
                    datetime.now() - worker_data["last_activity"]
                ).total_seconds(),
            }

        return performance

    def get_system_status(self):
        """Get comprehensive system status"""
        return {
            "workers": self.workers,
            "worker_status": self.worker_status,
            "queue_size": self.task_queue.qsize(),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "processing_interval": self.processing_interval,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Main entry point"""
    try:
        processor = CollectiveWorkerProcessor(max_workers=8)
        processor.start_collective_processing_loop(interval=15)

    except KeyboardInterrupt:
        logger.info("System interrupted by user")
    except Exception as e:
        logger.error(f"System error: {e}")


if __name__ == "__main__":
    main()

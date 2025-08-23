#!/usr/bin/env python3
"""
Dynamic Worker Coordinator - Manages collective workers and enables collaboration
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
from typing import Any, Dict, List, Optional

# Add the core directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from todo_master_reader import TodoMasterReader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DynamicWorkerCoordinator:
    """Coordinates dynamic workers for collaborative task processing"""

    def __init__(self):
        self.todo_reader = TodoMasterReader()
        self.coordination_interval = 5  # Coordinate every 5 seconds
        self.coordinator_active = True

        # Worker management
        self.active_workers = {}  # worker_id -> worker_info
        self.worker_capabilities = {}  # worker_id -> capabilities
        self.worker_status = {}  # worker_id -> status

        # Task management
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}  # task_id -> task_info
        self.completed_tasks = []
        self.collaborative_tasks = {}  # task_id -> [worker_ids]

        # Performance tracking
        self.worker_performance = {}
        self.system_metrics = {
            "total_workers": 0,
            "active_workers": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "collaboration_rate": 0.0,
            "last_update": datetime.now().isoformat(),
        }

        # Create coordination directory
        self.coordination_dir = current_dir / "coordination"
        self.coordination_dir.mkdir(exist_ok=True)

        logger.info("Dynamic Worker Coordinator initialized")

    def start_coordination_loop(self):
        """Start the continuous coordination loop"""
        logger.info("Starting dynamic worker coordination loop")

        try:
            while self.coordinator_active:
                start_time = time.time()

                # Discover and register workers
                self._discover_workers()

                # Analyze available tasks
                self._analyze_available_tasks()

                # Assign tasks to workers
                self._assign_tasks_to_workers()

                # Monitor collaborative progress
                self._monitor_collaborative_progress()

                # Update system metrics
                self._update_system_metrics()

                # Calculate processing time and sleep
                processing_time = time.time() - start_time
                sleep_time = max(0, self.coordination_interval - processing_time)

                logger.info(
                    f"Coordination took {processing_time:.2f}s, sleeping for {sleep_time:.2f}s"
                )
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Worker coordination loop interrupted by user")
        except Exception as e:
            logger.error(f"Error in worker coordination loop: {e}")

    def _discover_workers(self):
        """Discover and register available workers"""
        try:
            # Scan for worker processes
            import psutil

            for proc in psutil.process_iter(["pid", "name", "cmdline", "cwd"]):
                try:
                    if proc.info[
                        "cmdline"
                    ] and "collective_worker_processor.py" in " ".join(
                        proc.info["cmdline"]
                    ):

                        worker_id = f"worker_{proc.pid}"

                        if worker_id not in self.active_workers:
                            # Register new worker
                            self.active_workers[worker_id] = {
                                "pid": proc.pid,
                                "discovered_at": datetime.now(),
                                "status": "available",
                                "current_task": None,
                                "tasks_completed": 0,
                                "collaboration_count": 0,
                            }

                            # Assign capabilities based on worker characteristics
                            self.worker_capabilities[worker_id] = (
                                self._assign_worker_capabilities(proc)
                            )

                            logger.info(
                                f"Discovered new worker: {worker_id} (PID: {proc.pid})"
                            )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Remove workers that are no longer running
            active_worker_ids = list(self.active_workers.keys())
            for worker_id in active_worker_ids:
                try:
                    pid = self.active_workers[worker_id]["pid"]
                    if not psutil.pid_exists(pid):
                        del self.active_workers[worker_id]
                        if worker_id in self.worker_capabilities:
                            del self.worker_capabilities[worker_id]
                        logger.info(f"Removed inactive worker: {worker_id}")
                except:
                    pass

        except Exception as e:
            logger.error(f"Error discovering workers: {e}")

    def _assign_worker_capabilities(self, proc):
        """Assign capabilities to a worker based on its characteristics"""
        try:
            # Analyze process characteristics
            memory_info = proc.memory_info()
            cpu_percent = proc.cpu_percent()

            capabilities = {
                "memory_available": memory_info.rss / 1024 / 1024,  # MB
                "cpu_efficiency": 100 - cpu_percent,
                "can_handle_complex": memory_info.rss > 15 * 1024 * 1024,  # > 15MB
                "can_collaborate": True,
                "specializations": [],
            }

            # Add specializations based on memory and CPU
            if capabilities["memory_available"] > 20:
                capabilities["specializations"].extend(
                    ["large_tasks", "data_processing"]
                )

            if capabilities["cpu_efficiency"] > 80:
                capabilities["specializations"].extend(
                    ["cpu_intensive", "parallel_processing"]
                )

            # Add collaboration capabilities
            capabilities["specializations"].extend(["collaboration", "task_sharing"])

            return capabilities

        except Exception as e:
            logger.error(f"Error assigning worker capabilities: {e}")
            return {
                "memory_available": 15,
                "cpu_efficiency": 70,
                "can_handle_complex": True,
                "can_collaborate": True,
                "specializations": ["basic", "collaboration"],
            }

    def _analyze_available_tasks(self):
        """Analyze available tasks and determine collaboration opportunities"""
        try:
            pending_todos = self.todo_reader.get_pending_todos()

            for todo in pending_todos:
                todo_id = todo.get("id", "unknown")

                if todo_id not in self.active_tasks:
                    # Analyze task complexity and collaboration potential
                    collaboration_score = self._calculate_collaboration_score(todo)

                    if collaboration_score > 0.7:  # High collaboration potential
                        # Break down into collaborative subtasks
                        subtasks = self._create_collaborative_subtasks(todo)

                        self.active_tasks[todo_id] = {
                            "todo": todo,
                            "subtasks": subtasks,
                            "status": "pending",
                            "assigned_workers": [],
                            "collaboration_score": collaboration_score,
                            "created_at": datetime.now(),
                        }

                        # Add to task queue with priority
                        priority = self._calculate_task_priority(todo)
                        self.task_queue.put((priority, todo_id))

                        logger.info(
                            f"Created collaborative task: {todo_id} (score: {collaboration_score:.2f})"
                        )

                    elif todo_id not in self.active_tasks:
                        # Regular task
                        self.active_tasks[todo_id] = {
                            "todo": todo,
                            "subtasks": [todo],
                            "status": "pending",
                            "assigned_workers": [],
                            "collaboration_score": 0.0,
                            "created_at": datetime.now(),
                        }

                        priority = self._calculate_task_priority(todo)
                        self.task_queue.put((priority, todo_id))

        except Exception as e:
            logger.error(f"Error analyzing available tasks: {e}")

    def _calculate_collaboration_score(self, todo):
        """Calculate how suitable a task is for collaboration"""
        title = todo.get("title", "").lower()
        description = todo.get("description", "").lower()

        collaboration_indicators = [
            "multiple",
            "several",
            "all",
            "fix all",
            "refactor",
            "database",
            "api",
            "integration",
            "performance",
            "security",
            "migration",
            "upgrade",
            "restructure",
            "reorganize",
            "files",
            "components",
            "modules",
            "systems",
        ]

        score = 0.0

        # Check for collaboration indicators
        for indicator in collaboration_indicators:
            if indicator in title or indicator in description:
                score += 0.1

        # Check description length (longer = more complex = more collaboration potential)
        if len(description) > 100:
            score += 0.2

        # Check for specific collaboration patterns
        if "fix all" in title:
            score += 0.3
        if "refactor" in title:
            score += 0.2
        if "database" in title or "api" in title:
            score += 0.2

        return min(score, 1.0)

    def _create_collaborative_subtasks(self, todo):
        """Create collaborative subtasks for a complex TODO"""
        title = todo.get("title", "")
        description = todo.get("description", "")

        subtasks = []

        # Create different types of subtasks based on complexity
        todo_id = todo.get("id", "unknown")

        if "fix all" in title.lower():
            # File-based breakdown
            subtasks = [
                {
                    "id": f"{todo_id}_analysis",
                    "title": "Analyze Issues",
                    "type": "analysis",
                    "estimated_duration": "15min",
                },
                {
                    "id": f"{todo_id}_planning",
                    "title": "Create Fix Plan",
                    "type": "planning",
                    "estimated_duration": "20min",
                },
                {
                    "id": f"{todo_id}_implementation",
                    "title": "Implement Fixes",
                    "type": "implementation",
                    "estimated_duration": "45min",
                },
                {
                    "id": f"{todo_id}_testing",
                    "title": "Test Fixes",
                    "type": "testing",
                    "estimated_duration": "30min",
                },
                {
                    "id": f"{todo_id}_validation",
                    "title": "Validate Results",
                    "type": "validation",
                    "estimated_duration": "15min",
                },
            ]
        elif "refactor" in title.lower():
            # Refactoring breakdown
            subtasks = [
                {
                    "id": f"{todo_id}_assessment",
                    "title": "Code Assessment",
                    "type": "assessment",
                    "estimated_duration": "25min",
                },
                {
                    "id": f"{todo_id}_design",
                    "title": "New Design",
                    "type": "design",
                    "estimated_duration": "35min",
                },
                {
                    "id": f"{todo_id}_migration",
                    "title": "Code Migration",
                    "type": "migration",
                    "estimated_duration": "60min",
                },
                {
                    "id": f"{todo_id}_testing",
                    "title": "Regression Testing",
                    "type": "testing",
                    "estimated_duration": "40min",
                },
            ]
        else:
            # Generic breakdown
            subtasks = [
                {
                    "id": f"{todo_id}_research",
                    "title": "Research & Analysis",
                    "type": "research",
                    "estimated_duration": "20min",
                },
                {
                    "id": f"{todo_id}_planning",
                    "title": "Planning & Design",
                    "type": "planning",
                    "estimated_duration": "25min",
                },
                {
                    "id": f"{todo_id}_implementation",
                    "title": "Implementation",
                    "type": "implementation",
                    "estimated_duration": "50min",
                },
                {
                    "id": f"{todo_id}_testing",
                    "title": "Testing & Validation",
                    "type": "testing",
                    "estimated_duration": "30min",
                },
            ]

        # Add metadata
        for subtask in subtasks:
            subtask["status"] = "pending"
            subtask["assigned_worker"] = None
            subtask["created_at"] = datetime.now()
            subtask["parent_task"] = todo.get("id")

        return subtasks

    def _calculate_task_priority(self, todo):
        """Calculate task priority for queue ordering"""
        priority = 0

        # Higher priority for complex tasks
        if self._calculate_collaboration_score(todo) > 0.7:
            priority += 100

        # Priority based on title keywords
        title = todo.get("title", "").lower()
        if "urgent" in title or "critical" in title:
            priority += 200
        elif "high" in title:
            priority += 150
        elif "security" in title:
            priority += 180

        # Priority based on description length (longer = more complex = higher priority)
        description = todo.get("description", "")
        if len(description) > 200:
            priority += 50

        return priority

    def _assign_tasks_to_workers(self):
        """Assign tasks to available workers"""
        try:
            while not self.task_queue.empty():
                priority, task_id = self.task_queue.get()

                if task_id not in self.active_tasks:
                    continue

                task_info = self.active_tasks[task_id]

                if task_info["status"] != "pending":
                    continue

                # Find available workers
                available_workers = [
                    worker_id
                    for worker_id, worker_data in self.active_workers.items()
                    if worker_data["status"] == "available"
                ]

                if not available_workers:
                    # Put task back in queue
                    self.task_queue.put((priority, task_id))
                    break

                # Assign workers based on collaboration potential
                if (
                    task_info["collaboration_score"] > 0.7
                    and len(available_workers) >= 2
                ):
                    # Collaborative assignment
                    assigned_workers = self._assign_collaborative_workers(
                        task_info, available_workers
                    )

                    if assigned_workers:
                        task_info["assigned_workers"] = assigned_workers
                        task_info["status"] = "in_progress"

                        # Mark workers as busy
                        for worker_id in assigned_workers:
                            self.active_workers[worker_id]["status"] = "collaborating"
                            self.active_workers[worker_id]["current_task"] = task_id

                        # Initialize collaboration tracking
                        self.collaborative_tasks[task_id] = {
                            "workers": assigned_workers,
                            "subtask_progress": {},
                            "started_at": datetime.now(),
                        }

                        logger.info(
                            f"Assigned collaborative task {task_id} to workers: {assigned_workers}"
                        )

                else:
                    # Single worker assignment
                    worker_id = available_workers[0]
                    task_info["assigned_workers"] = [worker_id]
                    task_info["status"] = "in_progress"

                    # Mark worker as busy
                    self.active_workers[worker_id]["status"] = "working"
                    self.active_workers[worker_id]["current_task"] = task_id

                    logger.info(f"Assigned task {task_id} to worker: {worker_id}")

        except Exception as e:
            logger.error(f"Error assigning tasks to workers: {e}")

    def _assign_collaborative_workers(self, task_info, available_workers):
        """Assign multiple workers for collaborative tasks"""
        try:
            # Sort workers by capability score
            worker_scores = []
            for worker_id in available_workers:
                capabilities = self.worker_capabilities.get(worker_id, {})
                score = (
                    capabilities.get("memory_available", 15) / 20  # Memory score
                    + capabilities.get("cpu_efficiency", 70) / 100  # CPU score
                    + (
                        1 if capabilities.get("can_collaborate", False) else 0
                    )  # Collaboration bonus
                )
                worker_scores.append((score, worker_id))

            # Sort by score (highest first)
            worker_scores.sort(reverse=True)

            # Select top workers (2-4 workers for collaboration)
            num_workers = min(4, len(available_workers), len(task_info["subtasks"]))
            selected_workers = [
                worker_id for _, worker_id in worker_scores[:num_workers]
            ]

            return selected_workers

        except Exception as e:
            logger.error(f"Error assigning collaborative workers: {e}")
            return (
                available_workers[:2]
                if len(available_workers) >= 2
                else available_workers[:1]
            )

    def _monitor_collaborative_progress(self):
        """Monitor progress of collaborative tasks"""
        try:
            for task_id, task_info in self.active_tasks.items():
                if (
                    task_info["status"] == "in_progress"
                    and task_info["collaboration_score"] > 0.7
                ):

                    # Check if all subtasks are completed
                    all_completed = all(
                        subtask["status"] == "completed"
                        for subtask in task_info["subtasks"]
                    )

                    if all_completed:
                        # Mark task as completed
                        task_info["status"] = "completed"
                        task_info["completed_at"] = datetime.now()

                        # Free up workers
                        for worker_id in task_info["assigned_workers"]:
                            if worker_id in self.active_workers:
                                self.active_workers[worker_id]["status"] = "available"
                                self.active_workers[worker_id]["current_task"] = None
                                self.active_workers[worker_id]["tasks_completed"] += 1
                                self.active_workers[worker_id][
                                    "collaboration_count"
                                ] += 1

                        # Move to completed tasks
                        self.completed_tasks.append(task_info)

                        # Remove from active tasks
                        del self.active_tasks[task_id]

                        # Remove from collaborative tracking
                        if task_id in self.collaborative_tasks:
                            del self.collaborative_tasks[task_id]

                        logger.info(
                            f"Collaborative task {task_id} completed by {len(task_info['assigned_workers'])} workers"
                        )

        except Exception as e:
            logger.error(f"Error monitoring collaborative progress: {e}")

    def _update_system_metrics(self):
        """Update system performance metrics"""
        try:
            total_workers = len(self.active_workers)
            active_workers = sum(
                1 for w in self.active_workers.values() if w["status"] != "available"
            )
            total_tasks = len(self.active_tasks) + len(self.completed_tasks)
            completed_tasks = len(self.completed_tasks)

            # Calculate collaboration rate
            collaboration_count = sum(
                w.get("collaboration_count", 0) for w in self.active_workers.values()
            )
            collaboration_rate = (collaboration_count / max(total_workers, 1)) * 100

            self.system_metrics.update(
                {
                    "total_workers": total_workers,
                    "active_workers": active_workers,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "collaboration_rate": round(collaboration_rate, 2),
                    "last_update": datetime.now().isoformat(),
                }
            )

            # Save metrics to file
            metrics_file = self.coordination_dir / "system_metrics.json"
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(self.system_metrics, f, indent=2, default=str)

            logger.info(
                f"Updated system metrics: {active_workers}/{total_workers} workers active, {completed_tasks}/{total_tasks} tasks completed"
            )

        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")

    def get_coordinator_status(self):
        """Get coordinator status"""
        return {
            "coordinator_active": self.coordinator_active,
            "system_metrics": self.system_metrics,
            "active_workers": len(self.active_workers),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "collaborative_tasks": len(self.collaborative_tasks),
            "last_update": datetime.now().isoformat(),
        }

    def get_worker_details(self):
        """Get detailed worker information"""
        return {
            "workers": self.active_workers,
            "capabilities": self.worker_capabilities,
            "performance": self.worker_performance,
        }


def main():
    """Main entry point"""
    try:
        print("🎯 Dynamic Worker Coordinator Starting...")
        print("=" * 60)

        coordinator = DynamicWorkerCoordinator()

        # Display initial status
        status = coordinator.get_coordinator_status()
        print(f"📊 Coordinator Status:")
        for key, value in status.items():
            if key != "system_metrics":
                print(f"   {key}: {value}")

        print("\n🚀 Starting coordination loop...")
        print("   - Discovering and registering workers")
        print("   - Analyzing task collaboration potential")
        print("   - Assigning tasks to optimal workers")
        print("   - Monitoring collaborative progress")
        print("   - Scaling workers dynamically")
        print("\n⚠️  Press Ctrl+C to stop")

        # Start coordination loop
        coordinator.start_coordination_loop()

    except KeyboardInterrupt:
        print("\n🛑 Dynamic Worker Coordinator stopped by user")
    except Exception as e:
        print(f"❌ Dynamic Worker Coordinator error: {e}")
        logger.error(f"Coordinator error: {e}")


if __name__ == "__main__":
    main()

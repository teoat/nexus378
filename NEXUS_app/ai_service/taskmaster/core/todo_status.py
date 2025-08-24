TODO Status Tracker - Prevents overlapping implementations by agents
Tracks the next 10 unimplemented TODO items and their implementation status

import logging
from datetime import datetime

from .simple_registry import task_registry

logger = logging.getLogger(__name__)

class TODOStatusTracker:

            "has_overlap": False,
            "overlap_type": None,
            "conflicting_agent": None,
            "details": None,
        }

        # Get the TODO item
        todo = None
        for t in task_registry.priority_todos:
            if t["id"] == todo_id:
                todo = t
                break

        if not todo:
            overlap_info.update(
                {
                    "has_overlap": True,
                    "overlap_type": "todo_not_found",
                    "details": f"TODO {todo_id} not found",
                }
            )
            return overlap_info

        # Check if already assigned to another agent
        if todo["assigned_agent"] and todo["assigned_agent"] != agent_id:
            overlap_info.update(
                {
                    "has_overlap": True,
                    "overlap_type": "already_assigned",
                    "conflicting_agent": todo["assigned_agent"],
                    "details": f"TODO {todo_id} already assigned to {todo['assigned_agent']}",
                }
            )
            return overlap_info

        # Check if already implemented
        if todo["implementation_status"] == "implemented":
            overlap_info.update(
                {
                    "has_overlap": True,
                    "overlap_type": "already_implemented",
                    "conflicting_agent": todo.get("implemented_by"),
                    "details": f"TODO {todo_id} already implemented by {todo.get('implemented_by')}",
                }
            )
            return overlap_info

        # Check for similar tasks in progress
        similar_todos = [
            t
            for t in task_registry.priority_todos
            if t["id"] != todo_id
            and t["status"] == "in_progress"
            and self._are_todos_similar(todo, t)
        ]

        if similar_todos:
            overlap_info.update(
                {
                    "has_overlap": True,
                    "overlap_type": "similar_task_in_progress",
                    "conflicting_agent": similar_todos[0]["assigned_agent"],
                    "details": f"Similar task {similar_todos[0]['id']} in progress by {similar_todos[0]['assigned_agent']}",
                }
            )
            return overlap_info

        return overlap_info

    def _are_todos_similar(self, todo1: Dict[str, Any], todo2: Dict[str, Any]) -> bool:

        name1 = todo1["name"].lower()
        name2 = todo2["name"].lower()

        # Check for common keywords that might indicate overlap
        common_keywords = [
            "agent",
            "implementation",
            "setup",
            "configuration",
            "development",
        ]
        name_overlap = any(
            (keyword in name1 and keyword in name2 for keyword in common_keywords)
        )

        # Check capability overlap
        cap1 = set(todo1.get("required_capabilities", []))
        cap2 = set(todo2.get("required_capabilities", []))
        capability_overlap = len(cap1.intersection(cap2)) > 0

        # Check description similarity
        desc1 = todo1["description"].lower()
        desc2 = todo2["description"].lower()
        desc_overlap = any(
            word in desc1 and word in desc2
            for word in ["agent", "implementation", "algorithm", "system"]
        )

        return name_overlap or (capability_overlap and desc_overlap)

    def log_implementation_attempt(
        self, todo_id: str, agent_id: str, success: bool, details: str = None
    ):

            "timestamp": datetime.now().isoformat(),
            "todo_id": todo_id,
            "agent_id": agent_id,
            "success": success,
            "details": details or "",
            "overlap_check": self.check_implementation_overlap(todo_id, agent_id),
        }

        self.implementation_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.implementation_log) > 1000:
            self.implementation_log = self.implementation_log[-1000:]

        if success:
            logger.info(f"Implementation logged: {todo_id} by {agent_id}")
        else:
            logger.warning(
                f"Failed implementation logged: {todo_id} by {agent_id} - {details}",
            )

    def get_unimplemented_todos(self) -> List[Dict[str, Any]]:

            if todo["implementation_status"] == "unimplemented"
        ]

    def get_implementation_summary(self) -> Dict[str, Any]:

            [t for t in task_registry.priority_todos if t["status"] == "in_progress"],
        )
        completed = len(
            [t for t in task_registry.priority_todos if t["status"] == "completed"],
        )

        return {
            "total_todos": total_todos,
            "unimplemented": unimplemented,
            "in_progress": in_progress,
            "completed": completed,
            "implementation_rate": (
                round((completed / total_todos * 100), 2) if total_todos > 0 else 0
            ),
            "last_updated": datetime.now().isoformat(),
        }

    def get_agent_workload_summary(self) -> Dict[str, Any]:

            if todo["assigned_agent"]:
                agent_id = todo["assigned_agent"]
                if agent_id not in agent_workloads:
                    agent_workloads[agent_id] = {
                        "total_tasks": 0,
                        "in_progress": 0,
                        "completed": 0,
                        "avg_progress": 0.0,
                    }

                agent_workloads[agent_id]["total_tasks"] += 1

                if todo["status"] == "in_progress":
                    agent_workloads[agent_id]["in_progress"] += 1
                elif todo["status"] == "completed":
                    agent_workloads[agent_id]["completed"] += 1

                # Calculate average progress
                current_avg = agent_workloads[agent_id]["avg_progress"]
                total_tasks = agent_workloads[agent_id]["total_tasks"]
                agent_workloads[agent_id]["avg_progress"] = (
                    current_avg * (total_tasks - 1) + todo["progress"]
                ) / total_tasks

        return agent_workloads

# Global TODO status tracker instance
todo_status_tracker = TODOStatusTracker()

#!/usr/bin/env python3
"""
Smart TODO Automation System with Task Master Integration
- Only works on 3 TODOs at a time
- Integrates with Task Master for TODO management
- Breaks down complex tasks into simpler TODOs
- Enables parallel collaborative work
- Auto-loads new TODOs from Task Master
"""

import json
import logging
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import asyncio

logger = logging.getLogger(__name__)

class TodoComplexity(Enum):
    """Complexity levels for TODOs"""
    SIMPLE = "simple"           # 1-2 hours
    MEDIUM = "medium"           # 3-6 hours
    COMPLEX = "complex"         # 7-12 hours
    EPIC = "epic"               # 12+ hours

class TodoStatus(Enum):
    """Status of TODOs in the system"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

@dataclass
class SmartTodo:
    """Smart TODO item with complexity and breakdown capabilities"""
    id: str
    title: str
    description: str
    complexity: TodoComplexity
    estimated_hours: float
    status: TodoStatus
    priority: int  # 1-5, where 1 is highest
    category: str
    dependencies: List[str]
    tags: List[str]
    parent_id: Optional[str] = None
    subtodos: List[str] = None  # IDs of subtodos
    assigned_agents: List[str] = None
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    mcp_session_id: Optional[str] = None
    task_master_id: Optional[str] = None  # ID in Task Master system

class TaskMasterIntegration:
    """Integration with Task Master system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.task_master_config = self._find_task_master_config()
        
    def _find_task_master_config(self) -> Optional[Path]:
        """Find Task Master configuration files"""
        possible_paths = [
            self.project_root / ".taskmaster",
            self.project_root / "taskmaster",
            self.project_root / "tasks"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def get_available_todos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get available TODOs from Task Master"""
        try:
            # Try to use task-master CLI if available
            result = subprocess.run(
                ["task-master", "list", "--status", "pending", "--limit", str(limit)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                # Parse CLI output and convert to TODO format
                return self._parse_task_master_output(result.stdout)
            else:
                # Fallback to file-based TODO discovery
                return self._discover_todos_from_files(limit)
                
        except FileNotFoundError:
            # Task Master CLI not available, use file discovery
            return self._discover_todos_from_files(limit)
    
    def _parse_task_master_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse Task Master CLI output"""
        todos = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('---'):
                # Parse TODO line (simplified parsing)
                parts = line.split('|')
                if len(parts) >= 3:
                    todo = {
                        "id": parts[0].strip(),
                        "title": parts[1].strip(),
                        "status": parts[2].strip(),
                        "priority": "medium",  # Default priority
                        "complexity": "medium"  # Default complexity
                    }
                    todos.append(todo)
        
        return todos
    
    def _discover_todos_from_files(self, limit: int) -> List[Dict[str, Any]]:
        """Discover TODOs from project files when Task Master is not available"""
        todos = []
        
        # Look for common TODO patterns in code files
        todo_patterns = [
            r"#\s*TODO[:\s]+(.+)",
            r"//\s*TODO[:\s]+(.+)",
            r"<!--\s*TODO[:\s]+(.+)",
            r"#\s*FIXME[:\s]+(.+)",
            r"//\s*FIXME[:\s]+(.+)"
        ]
        
        code_extensions = (
    ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php']
)
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in todo_patterns:
                        import re
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if len(todos) >= limit:
                                break
                            
                            todo = {
                                "id": str(uuid.uuid4()),
                                "title": match.strip(),
                                "status": "pending",
                                "priority": "medium",
                                "complexity": "medium",
                                "file": str(file_path.relative_to(self.project_root))
                            }
                            todos.append(todo)
                    
                    if len(todos) >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
        
        return todos
    
    def mark_todo_in_progress(self, todo_id: str, agent_id: str) -> bool:
        """Mark a TODO as in progress in Task Master"""
        try:
            # Try to use task-master CLI
            result = subprocess.run(
                ["task-master", "set-status", "--id", todo_id, "--status", "in-progress"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info(f"Marked TODO {todo_id} as in-progress in Task Master")
                return True
            else:
                logger.warning(
    f"Failed to mark TODO {todo_id} in Task Master: {result.stderr}",
)
                return False
                
        except FileNotFoundError:
            logger.warning("Task Master CLI not available, cannot mark TODO status")
            return False
    
    def mark_todo_complete(self, todo_id: str) -> bool:
        """Mark a TODO as complete in Task Master"""
        try:
            # Try to use task-master CLI
            result = subprocess.run(
                ["task-master", "set-status", "--id", todo_id, "--status", "done"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info(f"Marked TODO {todo_id} as done in Task Master")
                return True
            else:
                logger.warning(
    f"Failed to mark TODO {todo_id} as done in Task Master: {result.stderr}",
)
                return False
                
        except FileNotFoundError:
            logger.warning("Task Master CLI not available, cannot mark TODO status")
            return False

class TodoBreakdownEngine:
    """Engine for breaking down complex TODOs into simpler ones"""
    
    def __init__(self):
        self.breakdown_rules = self._initialize_breakdown_rules()
    
    def _initialize_breakdown_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rules for breaking down TODOs by category"""
        return {
            "infrastructure": {
                "max_subtodo_hours": 4.0,
                "breakdown_patterns": ["setup", "configure", "test", "deploy"],
                "complexity_threshold": 6.0
            },
            "ai_agent": {
                "max_subtodo_hours": 6.0,
                "breakdown_patterns": ["data_prep", "model_training", "evaluation", "integration"],
                "complexity_threshold": 8.0
            },
            "database": {
                "max_subtodo_hours": 3.0,
                "breakdown_patterns": ["schema_design", "implementation", "migration", "testing"],
                "complexity_threshold": 5.0
            },
            "api": {
                "max_subtodo_hours": 4.0,
                "breakdown_patterns": ["endpoint_design", "implementation", "testing", "documentation"],
                "complexity_threshold": 6.0
            },
            "frontend": {
                "max_subtodo_hours": 5.0,
                "breakdown_patterns": ["component_design", "implementation", "styling", "testing"],
                "complexity_threshold": 7.0
            },
            "testing": {
                "max_subtodo_hours": 2.0,
                "breakdown_patterns": ["unit_tests", "integration_tests", "e2e_tests", "performance_tests"],
                "complexity_threshold": 4.0
            }
        }
    
    def should_breakdown(self, todo: SmartTodo) -> bool:
        """Determine if a TODO should be broken down"""
        rules = self.breakdown_rules.get(todo.category, {})
        threshold = rules.get("complexity_threshold", 6.0)
        
        return todo.estimated_hours > threshold
    
    def breakdown_todo(self, todo: SmartTodo) -> List[SmartTodo]:
        """Break down a complex TODO into simpler subtodos"""
        if not self.should_breakdown(todo):
            return []
        
        rules = self.breakdown_rules.get(todo.category, {})
        max_hours = rules.get("max_subtodo_hours", 4.0)
        patterns = rules.get(
    "breakdown_patterns",
    ["plan",
    "implement",
    "test",
    "deploy"]
)
        
        subtodos = []
        remaining_hours = todo.estimated_hours
        pattern_index = 0
        
        while remaining_hours > 0 and pattern_index < len(patterns):
            # Calculate hours for this subtodo
            if remaining_hours <= max_hours:
                subtodo_hours = remaining_hours
            else:
                subtodo_hours = max_hours
            
            # Create subtodo
            subtodo = SmartTodo(
                id=str(uuid.uuid4()),
                title=f"{todo.title} - {patterns[pattern_index].replace('_', ' ').title()}",
                description=f"{patterns[pattern_index].replace('_', ' ').title()} phase of {todo.title}",
                complexity=self._calculate_complexity(subtodo_hours),
                estimated_hours=subtodo_hours,
                status=TodoStatus.PENDING,
                priority=todo.priority,
                category=todo.category,
                dependencies=[],
                tags=todo.tags + [f"subtask_of_{todo.id}"],
                parent_id=todo.id,
                subtodos=[],
                assigned_agents=[],
                created_at=time.time(),
                mcp_session_id=todo.mcp_session_id,
                task_master_id=todo.task_master_id
            )
            
            subtodos.append(subtodo)
            remaining_hours -= subtodo_hours
            pattern_index += 1
        
        return subtodos
    
    def _calculate_complexity(self, hours: float) -> TodoComplexity:
        """Calculate complexity based on estimated hours"""
        if hours <= 2:
            return TodoComplexity.SIMPLE
        elif hours <= 6:
            return TodoComplexity.MEDIUM
        elif hours <= 12:
            return TodoComplexity.COMPLEX
        else:
            return TodoComplexity.EPIC

class MCPLogger:
    """Model Context Protocol Logger for tracking agent activities"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.agent_activities: Dict[str, List[Dict[str, Any]]] = {}
        self.implementation_locks: Dict[str, str] = {}
        self.todo_assignments: Dict[str, str] = {}  # TODO ID -> Agent ID
    
    def create_session(self, session_id: str, description: str):
        """Create a new MCP session"""
        self.sessions[session_id] = {
            "id": session_id,
            "description": description,
            "created": time.time(),
            "status": "active",
            "active_todos": [],
            "completed_todos": [],
            "agent_assignments": {}
        }
        logger.info(f"MCP Session created: {session_id} - {description}")
    
    def assign_todo_to_agent(
        self,
        session_id: str,
        todo_id: str,
        agent_id: str
    ):
        """Assign a TODO to an agent for implementation"""
        if todo_id in self.implementation_locks:
            logger.warning(
    f"TODO {todo_id} already assigned to {self.implementation_locks[todo_id]}",
)
            return False
        
        self.implementation_locks[todo_id] = agent_id
        self.todo_assignments[todo_id] = agent_id
        
        if session_id in self.sessions:
            self.sessions[session_id]["agent_assignments"][todo_id] = agent_id
            if todo_id not in self.sessions[session_id]["active_todos"]:
                self.sessions[session_id]["active_todos"].append(todo_id)
            logger.info(f"TODO {todo_id} assigned to agent {agent_id}")
            return True
        return False
    
    def log_todo_start(self, session_id: str, agent_id: str, todo_id: str):
        """Log start of TODO implementation"""
        if session_id in self.sessions:
            activity = {
                "timestamp": time.time(),
                "agent_id": agent_id,
                "todo_id": todo_id,
                "action": "todo_start",
                "status": "in_progress"
            }
            
            if agent_id not in self.agent_activities:
                self.agent_activities[agent_id] = []
            self.agent_activities[agent_id].append(activity)
            
            logger.info(f"Agent {agent_id} started working on TODO {todo_id}")
    
    def log_todo_complete(self, session_id: str, agent_id: str, todo_id: str):
        """Log completion of TODO implementation"""
        if session_id in self.sessions:
            if todo_id in self.sessions[session_id]["active_todos"]:
                self.sessions[session_id]["active_todos"].remove(todo_id)
            
            if todo_id not in self.sessions[session_id]["completed_todos"]:
                self.sessions[session_id]["completed_todos"].append(todo_id)
            
            # Release the lock
            if todo_id in self.implementation_locks:
                del self.implementation_locks[todo_id]
            if todo_id in self.todo_assignments:
                del self.todo_assignments[todo_id]
            
            activity = {
                "timestamp": time.time(),
                "agent_id": agent_id,
                "todo_id": todo_id,
                "action": "todo_complete",
                "status": "completed"
            }
            
            if agent_id not in self.agent_activities:
                self.agent_activities[agent_id] = []
            self.agent_activities[agent_id].append(activity)
            
            logger.info(f"Agent {agent_id} completed TODO {todo_id}")
    
    def get_available_todos(self, session_id: str) -> List[str]:
        """Get list of available (unassigned) TODOs"""
        if session_id not in self.sessions:
            return []
        
        assigned_todos = set(self.implementation_locks.keys())
        all_todos = set(self.sessions[session_id]["active_todos"])
        
        return list(all_todos - assigned_todos)
    
    def get_agent_todos(self, agent_id: str) -> List[str]:
        """Get TODOs assigned to a specific agent"""
        return [todo_id for todo_id, assigned_agent in self.todo_assignments.items() 
                if assigned_agent == agent_id]

class SmartTodoAutomation:
    """Smart TODO automation system with 3-TODO limit and Task Master integration"""
    
    def __init__(self, project_root: str = None, max_active_todos: int = 3):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.max_active_todos = max_active_todos
        self.task_master = TaskMasterIntegration(str(self.project_root))
        self.breakdown_engine = TodoBreakdownEngine()
        self.mcp_logger = MCPLogger()
        
        # Active TODOs in the system
        self.active_todos: Dict[str, SmartTodo] = {}
        self.completed_todos: Dict[str, SmartTodo] = {}
        self.available_todos: List[SmartTodo] = []
        
        # Agent management
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.agent_workloads: Dict[str, int] = {}
        
        logger.info(
    f"Smart TODO Automation initialized with max {max_active_todos} active TODOs",
)
    
    def start_automation_session(
        self,
        description: str = "Smart TODO Automation Session"
    ):
        """Start a new automation session"""
        session_id = str(uuid.uuid4())
        self.mcp_logger.create_session(session_id, description)
        logger.info(f"Automation session started: {session_id}")
        return session_id
    
    def load_todos_from_task_master(self, session_id: str, limit: int = 10) -> int:
        """Load TODOs from Task Master system"""
        logger.info("Loading TODOs from Task Master...")
        
        # Get available TODOs from Task Master
        raw_todos = self.task_master.get_available_todos(limit)
        
        loaded_count = 0
        for raw_todo in raw_todos:
            if len(self.available_todos) >= limit:
                break
            
            # Convert to SmartTodo format
            smart_todo = SmartTodo(
                id=raw_todo.get("id", str(uuid.uuid4())),
                title=raw_todo.get("title", "Untitled TODO"),
                description=raw_todo.get("description", raw_todo.get("title", "")),
                complexity=self._estimate_complexity(raw_todo),
                estimated_hours=self._estimate_hours(raw_todo),
                status=TodoStatus.PENDING,
                priority=self._parse_priority(raw_todo.get("priority", "medium")),
                category=raw_todo.get("category", "general"),
                dependencies=raw_todo.get("dependencies", []),
                tags=raw_todo.get("tags", []),
                created_at=time.time(),
                mcp_session_id=session_id,
                task_master_id=raw_todo.get("id")
            )
            
            self.available_todos.append(smart_todo)
            loaded_count += 1
        
        logger.info(f"Loaded {loaded_count} TODOs from Task Master")
        return loaded_count
    
    def _estimate_complexity(self, raw_todo: Dict[str, Any]) -> TodoComplexity:
        """Estimate complexity from raw TODO data"""
        complexity = raw_todo.get("complexity", "medium")
        
        if isinstance(complexity, str):
            try:
                return TodoComplexity(complexity.lower())
            except ValueError:
                pass
        
        # Estimate from other fields
        hours = self._estimate_hours(raw_todo)
        if hours <= 2:
            return TodoComplexity.SIMPLE
        elif hours <= 6:
            return TodoComplexity.MEDIUM
        elif hours <= 12:
            return TodoComplexity.COMPLEX
        else:
            return TodoComplexity.EPIC
    
    def _estimate_hours(self, raw_todo: Dict[str, Any]) -> float:
        """Estimate hours from raw TODO data"""
        if "estimated_hours" in raw_todo:
            return float(raw_todo["estimated_hours"])
        
        # Estimate from complexity
        complexity = raw_todo.get("complexity", "medium")
        complexity_hours = {
            "simple": 2.0,
            "medium": 6.0,
            "complex": 10.0,
            "epic": 20.0
        }
        
        return complexity_hours.get(complexity.lower(), 6.0)
    
    def _parse_priority(self, priority: str) -> int:
        """Parse priority string to numeric value"""
        priority_map = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4,
            "lowest": 5
        }
        
        return priority_map.get(priority.lower(), 3)
    
    def activate_todos(self, session_id: str, count: int = None) -> int:
        """Activate TODOs from available pool to active pool"""
        if count is None:
            count = self.max_active_todos - len(self.active_todos)
        
        count = min(count, self.max_active_todos - len(self.active_todos))
        if count <= 0:
            return 0
        
        activated_count = 0
        
        # Sort available TODOs by priority and complexity
        sorted_todos = sorted(
            self.available_todos,
            key=lambda x: (x.priority, x.estimated_hours)
        )
        
        for todo in sorted_todos[:count]:
            # Check if TODO should be broken down
            if self.breakdown_engine.should_breakdown(todo):
                subtodos = self.breakdown_engine.breakdown_todo(todo)
                
                # Add subtodos to available pool
                for subtodo in subtodos:
                    self.available_todos.append(subtodo)
                
                # Mark original TODO as broken down
                todo.status = TodoStatus.BLOCKED
                todo.tags.append("broken_down")
                
                # Activate subtodos instead
                for subtodo in subtodos[:count - activated_count]:
                    if activated_count >= count:
                        break
                    
                    self._activate_single_todo(subtodo, session_id)
                    activated_count += 1
            else:
                if activated_count >= count:
                    break
                
                self._activate_single_todo(todo, session_id)
                activated_count += 1
        
        logger.info(f"Activated {activated_count} TODOs")
        return activated_count
    
    def _activate_single_todo(self, todo: SmartTodo, session_id: str):
        """Activate a single TODO"""
        # Remove from available pool
        if todo in self.available_todos:
            self.available_todos.remove(todo)
        
        # Add to active pool
        self.active_todos[todo.id] = todo
        
        # Add to MCP session
        if session_id in self.mcp_logger.sessions:
            self.mcp_logger.sessions[session_id]["active_todos"].append(todo.id)
        
        logger.info(f"Activated TODO: {todo.title}")
    
    def assign_todo_to_agent(
        self,
        session_id: str,
        todo_id: str,
        agent_id: str
    ):
        """Assign a TODO to an agent"""
        if todo_id not in self.active_todos:
            logger.warning(f"TODO {todo_id} not found in active TODOs")
            return False
        
        # Assign via MCP logger
        if self.mcp_logger.assign_todo_to_agent(session_id, todo_id, agent_id):
            # Update agent workload
            self.agent_workloads[agent_id] = self.agent_workloads.get(agent_id, 0) + 1
            
            # Mark TODO as in progress
            self.active_todos[todo_id].status = TodoStatus.IN_PROGRESS
            self.active_todos[todo_id].started_at = time.time()
            self.active_todos[todo_id].assigned_agents = [agent_id]
            
            # Mark in Task Master if available
            self.task_master.mark_todo_in_progress(todo_id, agent_id)
            
            logger.info(f"TODO {todo_id} assigned to agent {agent_id}")
            return True
        
        return False
    
    def complete_todo(self, session_id: str, todo_id: str, agent_id: str) -> bool:
        """Mark a TODO as complete"""
        if todo_id not in self.active_todos:
            logger.warning(f"TODO {todo_id} not found in active TODOs")
            return False
        
        # Log completion via MCP
        self.mcp_logger.log_todo_complete(session_id, agent_id, todo_id)
        
        # Move TODO to completed pool
        todo = self.active_todos.pop(todo_id)
        todo.status = TodoStatus.DONE
        todo.completed_at = time.time()
        self.completed_todos[todo_id] = todo
        
        # Update agent workload
        if agent_id in self.agent_workloads:
            self.agent_workloads[agent_id] = max(0, self.agent_workloads[agent_id] - 1)
        
        # Mark in Task Master if available
        self.task_master.mark_todo_complete(todo_id)
        
        logger.info(f"TODO {todo_id} completed by agent {agent_id}")
        return True
    
    def auto_load_new_todos(self, session_id: str) -> int:
        """Automatically load new TODOs when active pool has space"""
        available_slots = self.max_active_todos - len(self.active_todos)
        
        if available_slots > 0:
            # Load more TODOs from Task Master
            loaded_count = (
    self.load_todos_from_task_master(session_id, available_slots * 2)
)
            
            # Activate new TODOs
            activated_count = self.activate_todos(session_id, available_slots)
            
            logger.info(
                f"Auto-loaded {loaded_count} TODOs, activated {activated_count}"
            )
            return activated_count
        
        return 0
    
    def get_available_todos_for_agent(self, session_id: str, agent_id: str) -> List[SmartTodo]:
        """Get available TODOs that an agent can work on"""
        available_todo_ids = self.mcp_logger.get_available_todos(session_id)
        
        available_todos = []
        for todo_id in available_todo_ids:
            if todo_id in self.active_todos:
                todo = self.active_todos[todo_id]
                if todo.status == TodoStatus.PENDING:
                    available_todos.append(todo)
        
        return available_todos
    
    def get_system_status(self, session_id: str) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "session_id": session_id,
            "max_active_todos": self.max_active_todos,
            "active_todos_count": len(self.active_todos),
            "available_todos_count": len(self.available_todos),
            "completed_todos_count": len(self.completed_todos),
            "agent_workloads": self.agent_workloads.copy(),
            "mcp_session_status": self.mcp_logger.sessions.get(session_id, {}),
            "can_auto_load": len(self.active_todos) < self.max_active_todos
        }
    
    def run_automation_cycle(self, session_id: str) -> Dict[str, Any]:
        """Run one automation cycle"""
        logger.info("Starting automation cycle...")
        
        cycle_results = {
            "todos_activated": 0,
            "todos_completed": 0,
            "new_todos_loaded": 0,
            "cycle_duration": 0.0
        }
        
        start_time = time.time()
        
        # Auto-load new TODOs if needed
        if len(self.active_todos) < self.max_active_todos:
            cycle_results["new_todos_loaded"] = self.auto_load_new_todos(session_id)
        
        # Activate TODOs if we have available slots
        available_slots = self.max_active_todos - len(self.active_todos)
        if available_slots > 0:
            cycle_results["todos_activated"] = self.activate_todos(session_id, available_slots)
        
        cycle_results["cycle_duration"] = time.time() - start_time
        
        logger.info(f"Automation cycle completed: {cycle_results}")
        return cycle_results

# Example usage and testing
async def test_smart_todo_automation():
    """Test the Smart TODO Automation system"""
    print("🧪 Testing Smart TODO Automation System")
    print("=" * 60)
    
    # Create smart automation system
    smart_automation = SmartTodoAutomation(max_active_todos=3)
    
    # Start automation session
    session_id = (
    smart_automation.start_automation_session("Smart TODO Automation Testing")
)
    print(f"📋 Automation session started: {session_id}")
    
    # Load TODOs from Task Master
    print("\n📥 Loading TODOs from Task Master...")
    loaded_count = smart_automation.load_todos_from_task_master(session_id, 10)
    print(f"  Loaded {loaded_count} TODOs")
    
    # Activate TODOs
    print("\n🚀 Activating TODOs...")
    activated_count = smart_automation.activate_todos(session_id)
    print(f"  Activated {activated_count} TODOs")
    
    # Get system status
    print("\n📊 System Status:")
    status = smart_automation.get_system_status(session_id)
    print(
    f"  Active TODOs: {status['active_todos_count']}/{status['max_active_todos']}",
)
    print(f"  Available TODOs: {status['available_todos_count']}")
    print(f"  Completed TODOs: {status['completed_todos_count']}")
    
    # Simulate agent work
    print("\n🤖 Simulating agent work...")
    agent_id = "test_agent_1"
    
    # Get available TODOs for agent
    available_todos = (
    smart_automation.get_available_todos_for_agent(session_id, agent_id)
)
    if available_todos:
        todo = available_todos[0]
        print(f"  Agent {agent_id} can work on: {todo.title}")
        
        # Assign TODO to agent
        if smart_automation.assign_todo_to_agent(session_id, todo.id, agent_id):
            print(f"  ✅ TODO assigned to agent {agent_id}")
            
            # Complete TODO
            if smart_automation.complete_todo(session_id, todo.id, agent_id):
                print(f"  ✅ TODO completed by agent {agent_id}")
    
    # Run automation cycle
    print("\n🔄 Running automation cycle...")
    cycle_results = smart_automation.run_automation_cycle(session_id)
    print(f"  Cycle Results: {cycle_results}")
    
    # Final status
    print("\n📊 Final System Status:")
    final_status = smart_automation.get_system_status(session_id)
    print(
    f"  Active TODOs: {final_status['active_todos_count']}/{final_status['max_active_todos']}",
)
    print(f"  Available TODOs: {final_status['available_todos_count']}")
    print(f"  Completed TODOs: {final_status['completed_todos_count']}")
    
    print("\n✅ Smart TODO Automation test completed!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_smart_todo_automation())

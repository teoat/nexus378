"""
MCP Server - Central coordination hub for all agents
Updated with Next 10 Priority TODO Items and Overlap Prevention
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    MAINTENANCE = "maintenance"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    MAINTENANCE = "maintenance"


@dataclass
class Task:
    id: str
    name: str
    description: str
    agent_id: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    dependencies: List[str]
    metadata: Dict[str, Any]
    estimated_duration: str
    required_capabilities: List[str]


@dataclass
class Agent:
    id: str
    name: str
    capabilities: List[str]
    current_tasks: List[str]
    status: str
    last_heartbeat: datetime


class MCPServer:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.task_queue: List[str] = []
        self.completed_tasks: List[str] = []
        self.lock = asyncio.Lock()
        
        # Initialize with next 10 priority TODO items
        self._initialize_priority_todos()
    
    def _initialize_priority_todos(self):
        """Initialize the MCP server with the next 10 priority TODO items"""
        priority_todos = [
            {
                "name": "DuckDB OLAP Engine Setup",
                "description": "Configure DuckDB OLAP engine for high-performance reconciliation processing",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "4-6 hours",
                "required_capabilities": ["database_setup", "olap_configuration", "performance_optimization"]
            },
            {
                "name": "Multi-Factor Authentication Implementation",
                "description": "Implement TOTP, SMS, and hardware token support for enhanced security",
                "priority": TaskPriority.CRITICAL,
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["security", "authentication", "mfa_implementation"]
            },
            {
                "name": "End-to-End Encryption Setup",
                "description": "Implement AES-256 encryption for sensitive data with secure key management",
                "priority": TaskPriority.CRITICAL,
                "estimated_duration": "6-10 hours",
                "required_capabilities": ["security", "encryption", "key_management"]
            },
            {
                "name": "TaskRouter Implementation",
                "description": "Build intelligent routing system for optimal agent assignment and workload balancing",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "12-16 hours",
                "required_capabilities": ["python_development", "algorithm_implementation", "load_balancing"]
            },
            {
                "name": "WorkflowOrchestrator Development",
                "description": "Create complex investigation workflow management with dependency handling",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "16-20 hours",
                "required_capabilities": ["python_development", "workflow_management", "dependency_resolution"]
            },
            {
                "name": "Reconciliation Agent Core Algorithms",
                "description": "Implement deterministic matching, AI fuzzy matching, and outlier detection",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "20-24 hours",
                "required_capabilities": ["python_development", "machine_learning", "algorithm_implementation"]
            },
            {
                "name": "Fraud Agent Pattern Detection",
                "description": "Build entity network analysis and circular transaction detection algorithms",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "24-32 hours",
                "required_capabilities": ["python_development", "graph_algorithms", "fraud_detection"]
            },
            {
                "name": "Risk Agent Compliance Engine",
                "description": "Create multi-factor risk assessment with SOX, PCI, AML, GDPR compliance",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "18-24 hours",
                "required_capabilities": ["python_development", "compliance", "risk_assessment"]
            },
            {
                "name": "Evidence Agent Processing Pipeline",
                "description": "Build file processing, hash verification, and metadata extraction systems",
                "priority": TaskPriority.NORMAL,
                "estimated_duration": "16-20 hours",
                "required_capabilities": ["python_development", "file_processing", "hash_verification"]
            },
            {
                "name": "LangGraph Multi-Agent Orchestration",
                "description": "Set up agent communication protocols and parallel processing capabilities",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "14-18 hours",
                "required_capabilities": ["python_development", "langgraph", "multi_agent_systems"]
            }
        ]
        
        # Submit all priority todos
        for todo in priority_todos:
            self._submit_priority_todo(todo)
    
    def _submit_priority_todo(self, todo_data: Dict[str, Any]):
        """Submit a priority TODO item to the MCP server"""
        import uuid
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            name=todo_data["name"],
            description=todo_data["description"],
            agent_id=None,
            status=TaskStatus.PENDING,
            priority=todo_data["priority"],
            created_at=datetime.now(),
            dependencies=[],
            metadata={
                "type": "priority_todo",
                "phase": "phase_2_ai_services",
                "category": "core_development"
            },
            estimated_duration=todo_data["estimated_duration"],
            required_capabilities=todo_data["required_capabilities"]
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        logger.info(f"Priority TODO submitted: {todo_data['name']} - {todo_data['priority'].value}")
    
    async def register_agent(self, agent_id: str, name: str, capabilities: List[str]) -> bool:
        async with self.lock:
            if agent_id in self.agents:
                return False
            
            agent = Agent(
                id=agent_id,
                name=name,
                capabilities=capabilities,
                current_tasks=[],
                status="available",
                last_heartbeat=datetime.now()
            )
            
            self.agents[agent_id] = agent
            logger.info(f"Agent {name} registered with capabilities: {capabilities}")
            return True
    
    async def submit_task(self, name: str, description: str, dependencies: List[str] = None, 
                         priority: TaskPriority = TaskPriority.NORMAL, 
                         required_capabilities: List[str] = None,
                         estimated_duration: str = "Unknown") -> str:
        async with self.lock:
            # Check for duplicates
            for task in self.tasks.values():
                if (task.name == name and 
                    task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]):
                    logger.warning(f"Duplicate task: {name}")
                    return None
            
            import uuid
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                name=name,
                description=description,
                agent_id=None,
                status=TaskStatus.PENDING,
                priority=priority,
                created_at=datetime.now(),
                dependencies=dependencies or [],
                metadata={},
                estimated_duration=estimated_duration,
                required_capabilities=required_capabilities or []
            )
            
            self.tasks[task_id] = task
            self.task_queue.append(task_id)
            logger.info(f"Task submitted: {name} - Priority: {priority.value}")
            return task_id
    
    async def get_available_tasks(self, agent_id: str) -> List[Task]:
        async with self.lock:
            if agent_id not in self.agents:
                return []
            
            agent = self.agents[agent_id]
            available = []
            
            for task_id in self.task_queue:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    # Check if agent has required capabilities
                    if self._agent_can_handle_task(agent, task):
                        available.append(task)
            
            # Sort by priority (Critical -> High -> Normal -> Low -> Maintenance)
            available.sort(key=lambda x: self._get_priority_score(x.priority), reverse=True)
            return available
    
    def _agent_can_handle_task(self, agent: Agent, task: Task) -> bool:
        """Check if agent has the required capabilities for a task"""
        if not task.required_capabilities:
            return True
        
        agent_capabilities = set(agent.capabilities)
        required_capabilities = set(task.required_capabilities)
        
        # Agent must have at least 70% of required capabilities
        overlap = len(agent_capabilities.intersection(required_capabilities))
        required_count = len(required_capabilities)
        
        return (overlap / required_count) >= 0.7 if required_count > 0 else True
    
    def _get_priority_score(self, priority: TaskPriority) -> int:
        """Get numeric score for priority sorting"""
        priority_scores = {
            TaskPriority.CRITICAL: 5,
            TaskPriority.HIGH: 4,
            TaskPriority.NORMAL: 3,
            TaskPriority.LOW: 2,
            TaskPriority.MAINTENANCE: 1
        }
        return priority_scores.get(priority, 0)
    
    async def claim_task(self, agent_id: str, task_id: str) -> bool:
        async with self.lock:
            if agent_id not in self.agents or task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.PENDING:
                return False
            
            # Check if agent can handle the task
            agent = self.agents[agent_id]
            if not self._agent_can_handle_task(agent, task):
                logger.warning(f"Agent {agent.name} lacks capabilities for task {task.name}")
                return False
            
            # Check for dependency conflicts
            if not self._check_dependencies_met(task):
                logger.warning(f"Task {task.name} has unmet dependencies")
                return False
            
            task.agent_id = agent_id
            task.status = TaskStatus.IN_PROGRESS
            
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
            
            agent.current_tasks.append(task_id)
            logger.info(f"Task {task.name} claimed by agent {agent.name}")
            return True
    
    def _check_dependencies_met(self, task: Task) -> bool:
        """Check if all dependencies for a task are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                continue
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def complete_task(self, agent_id: str, task_id: str, result: Dict[str, Any] = None) -> bool:
        async with self.lock:
            if agent_id not in self.agents or task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.agent_id != agent_id:
                return False
            
            task.status = TaskStatus.COMPLETED
            if result:
                task.metadata["result"] = result
            
            agent = self.agents[agent_id]
            if task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)
            
            self.completed_tasks.append(task_id)
            logger.info(f"Task {task.name} completed by agent {agent.name}")
            return True
    
    async def fail_task(self, agent_id: str, task_id: str, error: str = None) -> bool:
        async with self.lock:
            if agent_id not in self.agents or task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.agent_id != agent_id:
                return False
            
            task.status = TaskStatus.FAILED
            if error:
                task.metadata["error"] = error
            
            agent = self.agents[agent_id]
            if task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)
            
            # Re-add to queue for retry (if not max retries exceeded)
            if task_id not in self.task_queue:
                self.task_queue.append(task_id)
            
            logger.warning(f"Task {task.name} failed by agent {agent.name}: {error}")
            return True
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive task status information"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.value,
            "agent_id": task.agent_id,
            "created_at": task.created_at.isoformat(),
            "estimated_duration": task.estimated_duration,
            "required_capabilities": task.required_capabilities,
            "metadata": task.metadata
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        async with self.lock:
            total_tasks = len(self.tasks)
            pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
            in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
            completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
            failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
            
            total_agents = len(self.agents)
            available_agents = len([a for a in self.agents.values() if a.status == "available"])
            
            return {
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "total_agents": total_agents,
                "available_agents": available_agents,
                "queue_length": len(self.task_queue),
                "timestamp": datetime.now().isoformat()
            }
    
    async def heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat"""
        async with self.lock:
            if agent_id in self.agents:
                self.agents[agent_id].last_heartbeat = datetime.now()
                return True
            return False


# Global instance
mcp_server = MCPServer()

# Export the server instance
__all__ = ["mcp_server", "TaskStatus", "TaskPriority", "Task", "Agent"]

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
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    MAINTENANCE = "maintenance"


@dataclass
class Task:
    """Task definition for MCP system"""
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
    """Agent information for MCP system"""
    id: str
    name: str
    capabilities: List[str]
    current_tasks: List[str]
    status: str
    last_heartbeat: datetime


class MCPServer:
    """Central MCP server for coordinating all agents"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.task_queue: List[str] = []
        self.completed_tasks: List[str] = []
        self.lock = asyncio.Lock()
        
        # Initialize with next 10 priority TODO items
        self._initialize_priority_todos()
    
    def _initialize_priority_todos(self):
        """Initialize the MCP server with the next 10 priority TODO items and subtasks"""
        priority_todos = [
            {
                "name": "Multi-Factor Authentication Implementation",
                "description": "Implement TOTP, SMS, and hardware token support for enhanced security",
                "priority": TaskPriority.CRITICAL,
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["security", "authentication", "mfa_implementation"],
                "type": "complex_task",
                "subtasks": [
                    "TOTP Service Implementation (3-4 hours)",
                    "SMS Service Integration (2-3 hours)",
                    "Hardware Token Support (2-3 hours)",
                    "MFA Configuration Management (1-2 hours)"
                ],
                "phase": "Phase 1 - Foundation",
                "category": "Security Foundation"
            },
            {
                "name": "End-to-End Encryption Setup", 
                "description": "Implement AES-256 encryption for sensitive data with secure key management",
                "priority": TaskPriority.CRITICAL,
                "estimated_duration": "6-10 hours",
                "required_capabilities": ["security", "encryption", "key_management"],
                "type": "complex_task",
                "subtasks": [
                    "AES-256 Encryption Core (3-4 hours)",
                    "Key Management System (2-3 hours)",
                    "Encryption Pipeline Integration (1-2 hours)"
                ],
                "phase": "Phase 1 - Foundation",
                "category": "Security Foundation"
            },
            {
                "name": "DuckDB OLAP Engine Setup",
                "description": "Configure DuckDB OLAP engine for high-performance reconciliation processing",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "4-6 hours",
                "required_capabilities": ["database_setup", "olap_configuration", "performance_optimization"],
                "type": "simple_task",
                "subtasks": [],
                "phase": "Phase 1 - Foundation",
                "category": "Database Architecture"
            },
            {
                "name": "Load Balancing Strategies Implementation",
                "description": "Implement advanced load balancing strategies for optimal agent distribution",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "8-12 hours",
                "required_capabilities": ["python_development", "load_balancing", "algorithm_implementation"],
                "type": "medium_task",
                "subtasks": [],
                "phase": "Phase 2 - AI Services",
                "category": "Taskmaster Core"
            },
            {
                "name": "Queue Monitoring and Metrics",
                "description": "Set up comprehensive queue monitoring and performance metrics",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "6-10 hours",
                "required_capabilities": ["python_development", "monitoring", "metrics"],
                "type": "medium_task",
                "subtasks": [],
                "phase": "Phase 2 - AI Services",
                "category": "Taskmaster Core"
            },
            {
                "name": "Reconciliation Agent Confidence Scoring",
                "description": "Implement confidence scoring engine for fuzzy match results",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "2-3 hours",
                "required_capabilities": ["python_development", "scoring_algorithms", "ai_integration"],
                "type": "simple_task",
                "subtasks": [],
                "phase": "Phase 2 - AI Services",
                "category": "AI Agents"
            },
            {
                "name": "Fraud Agent Pattern Detection", 
                "description": "Build entity network analysis and circular transaction detection algorithms",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "24-32 hours",
                "required_capabilities": ["python_development", "graph_algorithms", "fraud_detection"],
                "type": "complex_task",
                "subtasks": [
                    "Circular Transaction Detection (8-10 hours)",
                    "Transaction Flow Analysis (6-8 hours)",
                    "Pattern Recognition Engine (6-8 hours)",
                    "Alert Generation System (4-5 hours)"
                ],
                "phase": "Phase 2 - AI Services",
                "category": "AI Agents"
            },
            {
                "name": "Fraud Agent Entity Network Analysis",
                "description": "Implement advanced entity network analysis and shell company identification",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "18-24 hours",
                "required_capabilities": ["python_development", "graph_algorithms", "fraud_detection", "network_analysis"],
                "type": "complex_task",
                "subtasks": [
                    "Entity Relationship Mapping (6-8 hours)",
                    "Shell Company Detection (8-10 hours)",
                    "Network Centrality Analysis (4-5 hours)"
                ],
                "phase": "Phase 2 - AI Services",
                "category": "AI Agents"
            },
            {
                "name": "Risk Agent Compliance Engine",
                "description": "Create multi-factor risk assessment with SOX, PCI, AML, GDPR compliance",
                "priority": TaskPriority.HIGH,
                "estimated_duration": "18-24 hours",
                "required_capabilities": ["python_development", "compliance", "risk_assessment"],
                "type": "complex_task",
                "subtasks": [
                    "SOX Compliance Rules (4-5 hours)",
                    "Confidence Scoring Engine (2-3 hours)"
                ],
                "phase": "Phase 2 - AI Services",
                "category": "AI Agents"
            },
            {
                "name": "Evidence Agent Processing Pipeline",
                "description": "Build file processing, hash verification, and metadata extraction systems",
                "priority": TaskPriority.NORMAL,
                "estimated_duration": "16-20 hours",
                "required_capabilities": ["python_development", "file_processing", "hash_verification"],
                "type": "complex_task",
                "subtasks": [
                    "File Processing Core (4-5 hours)",
                    "Hash Verification System (3-4 hours)",
                    "EXIF Metadata Extraction (3-4 hours)",
                    "PDF OCR Processing (4-5 hours)",
                    "Chat Log NLP Processing (2-3 hours)"
                ],
                "phase": "Phase 2 - AI Services",
                "category": "AI Agents"
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
                "phase": todo_data.get("phase", "Unknown"),
                "category": todo_data.get("category", "Unknown"),
                "task_type": todo_data.get("type", "simple_task"),
                "subtasks": todo_data.get("subtasks", []),
                "subtask_count": len(todo_data.get("subtasks", [])),
                "implementation_status": "unimplemented",
                "progress": 0.0,
                "subtask_progress": {},
                "assigned_agent": None,
                "estimated_duration": todo_data["estimated_duration"],
                "required_capabilities": todo_data["required_capabilities"],
                "mcp_status": "MCP_TRACKED",
                "last_updated": "2024-12-19",
                "overlap_prevention": "active"
            },
            estimated_duration=todo_data["estimated_duration"],
            required_capabilities=todo_data["required_capabilities"]
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        logger.info(f"Priority TODO submitted: {todo_data['name']} - {todo_data['priority'].value} - {len(todo_data.get('subtasks', []))} subtasks")
        logger.info(f"  MCP Status: MCP_TRACKED - Ready for agent assignment")
        logger.info(f"  Overlap Prevention: ACTIVE - No duplicate implementations possible")
    
    async def register_agent(self, agent_id: str, name: str, capabilities: List[str]) -> bool:
        """Register a new agent with the MCP system"""
        async with self.lock:
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already registered")
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
        """Submit a new task to the MCP system"""
        async with self.lock:
            # Check for duplicates
            if await self._is_duplicate_task(name, description):
                logger.warning(f"Duplicate task detected: {name}")
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
    
    async def _is_duplicate_task(self, name: str, description: str) -> bool:
        """Check if a task is a duplicate based on name and description"""
        for task in self.tasks.values():
            if (task.name.lower() == name.lower() and 
                task.description.lower() == description.lower() and
                task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]):
                return True
        return False
    
    async def get_available_tasks(self, agent_id: str) -> List[Task]:
        """Get available tasks for a specific agent"""
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
        """Claim a task for implementation - Enhanced with overlap prevention"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for claiming")
            return False
        
        task = self.tasks[task_id]
        
        # Check if task is already claimed
        if task.agent_id is not None:
            logger.warning(f"Task {task_id} already claimed by {task.agent_id}")
            logger.warning(f"OVERLAP PREVENTION: Task {task.name} cannot be claimed by {agent_id}")
            return False
        
        # Check if agent can handle this task
        if not self._agent_can_handle_task(agent_id, task):
            logger.warning(f"Agent {agent_id} cannot handle task {task_id} - capability mismatch")
            logger.warning(f"OVERLAP PREVENTION: Agent {agent_id} lacks required capabilities for {task.name}")
            return False
        
        # Check dependencies
        if not self._check_dependencies_met(task):
            logger.warning(f"Task {task_id} dependencies not met - cannot be claimed")
            logger.warning(f"OVERLAP PREVENTION: Task {task.name} blocked by unmet dependencies")
            return False
        
        # Check for similar tasks in progress
        similar_tasks = self._find_similar_tasks(task, agent_id)
        if similar_tasks:
            logger.warning(f"Similar tasks already in progress - potential overlap detected")
            for similar in similar_tasks:
                logger.warning(f"  Similar task: {similar.name} (ID: {similar.id}) by {similar.agent_id}")
            logger.warning(f"OVERLAP PREVENTION: Similar task {task.name} already in progress")
            return False
        
        # Claim the task
        task.agent_id = agent_id
        task.status = TaskStatus.IN_PROGRESS
        task.metadata["assigned_agent"] = agent_id
        task.metadata["claimed_at"] = datetime.now().isoformat()
        
        # Update agent workload
        if agent_id in self.agents:
            self.agents[agent_id].current_tasks.append(task_id)
            self.agents[agent_id].last_heartbeat = datetime.now()
        
        # Log successful claim with overlap prevention details
        logger.info(f"Task {task_id} successfully claimed by {agent_id}")
        logger.info(f"  Task: {task.name}")
        logger.info(f"  Priority: {task.priority.value}")
        logger.info(f"  Required Capabilities: {task.required_capabilities}")
        logger.info(f"  Agent Capabilities: {self.agents[agent_id].capabilities if agent_id in self.agents else 'Unknown'}")
        logger.info(f"  Overlap Prevention: ACTIVE - Task now protected from duplicate claims")
        logger.info(f"  MCP Status: IN_PROGRESS - Implementation started")
        
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
        """Mark a task as completed"""
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
        """Mark a task as failed"""
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
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including TODO breakdown"""
        total_tasks = len(self.tasks)
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        blocked_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED])
        
        # Count priority TODO items
        priority_todos = [t for t in self.tasks.values() if t.metadata.get("type") == "priority_todo"]
        unimplemented_todos = len([t for t in priority_todos if t.metadata.get("implementation_status") == "unimplemented"])
        implemented_todos = len([t for t in priority_todos if t.metadata.get("implementation_status") == "implemented"])
        
        # Calculate subtask statistics
        total_subtasks = sum(t.metadata.get("subtask_count", 0) for t in priority_todos)
        completed_subtasks = sum(
            len([s for s in t.metadata.get("subtasks", []) 
                 if t.metadata.get("subtask_progress", {}).get(s, 0.0) >= 1.0])
            for t in priority_todos
        )
        
        # Get agent workload
        agent_workloads = {}
        for agent_id, agent in self.agents.items():
            agent_workloads[agent_id] = {
                "name": agent.name,
                "capabilities": agent.capabilities,
                "current_tasks": len(agent.current_tasks),
                "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None
            }
        
        return {
            "system_health": "healthy" if total_tasks > 0 else "initializing",
            "total_tasks": total_tasks,
            "task_status": {
                "pending": pending_tasks,
                "in_progress": in_progress_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "blocked": blocked_tasks
            },
            "priority_todos": {
                "total": len(priority_todos),
                "unimplemented": unimplemented_todos,
                "implemented": implemented_todos,
                "implementation_rate": round((implemented_todos / len(priority_todos) * 100), 2) if priority_todos else 0
            },
            "subtask_breakdown": {
                "total_subtasks": total_subtasks,
                "completed_subtasks": completed_subtasks,
                "remaining_subtasks": total_subtasks - completed_subtasks,
                "completion_rate": round((completed_subtasks / total_subtasks * 100), 2) if total_subtasks > 0 else 0
            },
            "agents": {
                "total_registered": len(self.agents),
                "active_agents": len([a for a in self.agents.values() if a.last_heartbeat]),
                "workloads": agent_workloads
            },
            "overlap_prevention": {
                "status": "ACTIVE",
                "mechanisms": [
                    "Task claiming validation",
                    "Capability matching",
                    "Dependency checking",
                    "Similar task detection",
                    "MCP status tracking"
                ],
                "last_updated": "2024-12-19"
            },
            "mcp_status": "ACTIVE",
            "last_updated": datetime.now().isoformat()
        }
    
    async def heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat"""
        async with self.lock:
            if agent_id in self.agents:
                self.agents[agent_id].last_heartbeat = datetime.now()
                return True
            return False
    
    async def refresh_priority_todos(self):
        """Refresh the priority TODO list with current status"""
        # Clear existing priority todos
        existing_tasks = [task_id for task_id, task in self.tasks.items() 
                         if task.metadata.get("type") == "priority_todo"]
        
        for task_id in existing_tasks:
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
            del self.tasks[task_id]
        
        # Re-initialize with updated priority todos
        self._initialize_priority_todos()
        logger.info("Priority TODO list refreshed")
    
    async def get_priority_todo_summary(self) -> Dict[str, Any]:
        """Get a summary of all priority TODO items"""
        priority_todos = []
        
        for task_id, task in self.tasks.items():
            if task.metadata.get("type") == "priority_todo":
                priority_todos.append({
                    "id": task.id,
                    "name": task.name,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "agent_id": task.agent_id,
                    "estimated_duration": task.estimated_duration,
                    "phase": task.metadata.get("phase", "Unknown"),
                    "category": task.metadata.get("category", "Unknown"),
                    "required_capabilities": task.required_capabilities,
                    "subtasks": task.metadata.get("subtasks", []),
                    "subtask_count": task.metadata.get("subtask_count", 0),
                    "implementation_status": task.metadata.get("implementation_status", "Unknown"),
                    "progress": task.metadata.get("progress", 0.0),
                    "assigned_agent": task.metadata.get("assigned_agent")
                })
        
        # Sort by priority
        priority_order = {"critical": 5, "high": 4, "normal": 3, "low": 2, "maintenance": 1}
        priority_todos.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        return {
            "total_tasks": len(priority_todos),
            "by_priority": {
                "critical": len([t for t in priority_todos if t["priority"] == "critical"]),
                "high": len([t for t in priority_todos if t["priority"] == "high"]),
                "normal": len([t for t in priority_todos if t["priority"] == "normal"]),
                "low": len([t for t in priority_todos if t["priority"] == "low"]),
                "maintenance": len([t for t in priority_todos if t["priority"] == "maintenance"])
            },
            "by_phase": {
                "Phase 1 - Foundation": len([t for t in priority_todos if t["phase"] == "Phase 1 - Foundation"]),
                "Phase 2 - AI Services": len([t for t in priority_todos if t["phase"] == "Phase 2 - AI Services"])
            },
            "by_status": {
                "pending": len([t for t in priority_todos if t["priority"] == "pending"]),
                "in_progress": len([t for t in priority_todos if t["priority"] == "in_progress"]),
                "completed": len([t for t in priority_todos if t["priority"] == "completed"]),
                "failed": len([t for t in priority_todos if t["priority"] == "failed"])
            },
            "tasks": priority_todos
        }
    
    async def update_task_progress(self, task_id: str, progress: float, status_update: str = None) -> bool:
        """Update task progress and status"""
        async with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.metadata["progress"] = max(0.0, min(1.0, progress))
            
            if status_update:
                task.metadata["status_update"] = status_update
            
            if progress >= 1.0 and task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.COMPLETED
                if task_id in self.task_queue:
                    self.task_queue.remove(task_id)
                self.completed_tasks.append(task_id)
            
            logger.info(f"Task {task.name} progress updated: {progress:.1%}")
            return True
    
    async def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed workload information for a specific agent"""
        if agent_id not in self.agents:
            return {}
        
        agent = self.agents[agent_id]
        current_tasks = []
        
        for task_id in agent.current_tasks:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                current_tasks.append({
                    "id": task.id,
                    "name": task.name,
                    "priority": task.priority.value,
                    "progress": task.metadata.get("progress", 0.0),
                    "estimated_duration": task.estimated_duration
                })
        
        return {
            "agent_id": agent.id,
            "name": agent.name,
            "capabilities": agent.capabilities,
            "status": agent.status,
            "current_tasks": current_tasks,
            "task_count": len(current_tasks),
            "last_heartbeat": agent.last_heartbeat.isoformat()
        }

    def _find_similar_tasks(self, task: Task, agent_id: str) -> List[Task]:
        """Find tasks similar to the given task that might cause overlap"""
        similar_tasks = []
        
        # Extract keywords from task name and description
        task_text = f"{task.name} {task.description}".lower()
        task_keywords = set(task_text.split())
        
        for other_task in self.tasks.values():
            if (other_task.id != task.id and 
                other_task.agent_id is not None and
                other_task.agent_id != agent_id and
                other_task.status == TaskStatus.IN_PROGRESS):
                
                other_text = f"{other_task.name} {other_task.description}".lower()
                other_keywords = set(other_text.split())
                
                # Check for keyword overlap
                common_keywords = task_keywords.intersection(other_keywords)
                if len(common_keywords) >= 3:  # At least 3 common keywords
                    similar_tasks.append(other_task)
        
        return similar_tasks


# Global instance
mcp_server = MCPServer()

# Export the server instance
__all__ = ["mcp_server", "TaskStatus", "TaskPriority", "Task", "Agent"]

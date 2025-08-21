"""
Model Context Protocol (MCP) System for Forensic Reconciliation App

This system provides centralized coordination for all AI agents to prevent
overlapping implementations and ensure efficient task distribution.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


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
    updated_at: datetime
    dependencies: List[str]
    metadata: Dict[str, Any]
    estimated_duration: Optional[timedelta]
    actual_duration: Optional[timedelta]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.estimated_duration:
            data['estimated_duration'] = str(self.estimated_duration)
        if self.actual_duration:
            data['actual_duration'] = str(self.actual_duration)
        return data


@dataclass
class Agent:
    """Agent information for MCP system"""
    id: str
    name: str
    capabilities: List[str]
    current_tasks: List[str]
    max_concurrent_tasks: int
    status: str  # "available", "busy", "offline"
    last_heartbeat: datetime
    performance_metrics: Dict[str, float]


class MCPServer:
    """Central MCP server for coordinating all agents"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.task_queue: List[str] = []
        self.completed_tasks: List[str] = []
        self.task_dependencies: Dict[str, Set[str]] = {}
        self.agent_capabilities: Dict[str, Set[str]] = {}
        self.lock = asyncio.Lock()
        
    async def register_agent(self, agent_id: str, name: str, capabilities: List[str], 
                           max_concurrent_tasks: int = 3) -> bool:
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
                max_concurrent_tasks=max_concurrent_tasks,
                status="available",
                last_heartbeat=datetime.now(),
                performance_metrics={}
            )
            
            self.agents[agent_id] = agent
            self.agent_capabilities[agent_id] = set(capabilities)
            logger.info(f"Agent {name} ({agent_id}) registered with capabilities: {capabilities}")
            return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the MCP system"""
        async with self.lock:
            if agent_id not in self.agents:
                return False
                
            # Reassign current tasks to other agents
            agent = self.agents[agent_id]
            for task_id in agent.current_tasks:
                await self._reassign_task(task_id, agent_id)
            
            del self.agents[agent_id]
            if agent_id in self.agent_capabilities:
                del self.agent_capabilities[agent_id]
                
            logger.info(f"Agent {agent_id} unregistered")
            return True
    
    async def submit_task(self, name: str, description: str, priority: TaskPriority = TaskPriority.MEDIUM,
                         dependencies: List[str] = None, metadata: Dict[str, Any] = None,
                         estimated_duration: Optional[timedelta] = None) -> str:
        """Submit a new task to the MCP system"""
        async with self.lock:
            # Check for duplicate tasks
            if await self._is_duplicate_task(name, description):
                logger.warning(f"Duplicate task detected: {name}")
                return None
            
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                name=name,
                description=description,
                agent_id=None,
                status=TaskStatus.PENDING,
                priority=priority,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                dependencies=dependencies or [],
                metadata=metadata or {},
                estimated_duration=estimated_duration,
                actual_duration=None
            )
            
            self.tasks[task_id] = task
            self.task_queue.append(task_id)
            
            # Update dependencies
            if dependencies:
                self.task_dependencies[task_id] = set(dependencies)
            
            logger.info(f"Task submitted: {name} (ID: {task_id})")
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
            available_tasks = []
            
            for task_id in self.task_queue:
                task = self.tasks[task_id]
                
                # Check if task is available and agent can handle it
                if (task.status == TaskStatus.PENDING and
                    task.agent_id is None and
                    len(agent.current_tasks) < agent.max_concurrent_tasks and
                    await self._can_agent_handle_task(agent_id, task_id)):
                    available_tasks.append(task)
            
            return available_tasks
    
    async def _can_agent_handle_task(self, agent_id: str, task_id: str) -> bool:
        """Check if an agent can handle a specific task"""
        task = self.tasks[task_id]
        agent_capabilities = self.agent_capabilities.get(agent_id, set())
        
        # Check if agent has required capabilities (if specified in metadata)
        required_capabilities = task.metadata.get('required_capabilities', [])
        if required_capabilities and not all(cap in agent_capabilities for cap in required_capabilities):
            return False
        
        # Check dependencies
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id not in self.completed_tasks:
                    return False
        
        return True
    
    async def claim_task(self, agent_id: str, task_id: str) -> bool:
        """Claim a task for execution by an agent"""
        async with self.lock:
            if agent_id not in self.agents or task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            agent = self.agents[agent_id]
            
            if (task.status != TaskStatus.PENDING or 
                task.agent_id is not None or
                len(agent.current_tasks) >= agent.max_concurrent_tasks):
                return False
            
            # Update task
            task.agent_id = agent_id
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now()
            
            # Update agent
            agent.current_tasks.append(task_id)
            agent.status = "busy" if len(agent.current_tasks) >= agent.max_concurrent_tasks else "available"
            
            # Remove from queue
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
            
            logger.info(f"Agent {agent_id} claimed task: {task.name}")
            return True
    
    async def complete_task(self, agent_id: str, task_id: str, 
                          result: Dict[str, Any] = None, 
                          actual_duration: Optional[timedelta] = None) -> bool:
        """Mark a task as completed"""
        async with self.lock:
            if agent_id not in self.agents or task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            agent = self.agents[agent_id]
            
            if task.agent_id != agent_id or task.status != TaskStatus.IN_PROGRESS:
                return False
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now()
            task.actual_duration = actual_duration
            if result:
                task.metadata['result'] = result
            
            # Update agent
            agent.current_tasks.remove(task_id)
            agent.status = "available" if len(agent.current_tasks) < agent.max_concurrent_tasks else "busy"
            
            # Add to completed tasks
            self.completed_tasks.append(task_id)
            
            # Update performance metrics
            if actual_duration:
                await self._update_agent_performance(agent_id, task_id, actual_duration)
            
            logger.info(f"Task completed: {task.name} by agent {agent_id}")
            return True
    
    async def _update_agent_performance(self, agent_id: str, task_id: str, duration: timedelta):
        """Update agent performance metrics"""
        agent = self.agents[agent_id]
        task = self.tasks[task_id]
        
        if 'task_completion_times' not in agent.performance_metrics:
            agent.performance_metrics['task_completion_times'] = []
        
        agent.performance_metrics['task_completion_times'].append(duration.total_seconds())
        
        # Keep only last 100 completion times
        if len(agent.performance_metrics['task_completion_times']) > 100:
            agent.performance_metrics['task_completion_times'] = agent.performance_metrics['task_completion_times'][-100:]
        
        # Calculate average completion time
        avg_time = sum(agent.performance_metrics['task_completion_times']) / len(agent.performance_metrics['task_completion_times'])
        agent.performance_metrics['average_completion_time'] = avg_time
    
    async def _reassign_task(self, task_id: str, old_agent_id: str):
        """Reassign a task to another available agent"""
        task = self.tasks[task_id]
        task.agent_id = None
        task.status = TaskStatus.PENDING
        task.updated_at = datetime.now()
        
        # Add back to queue
        if task_id not in self.task_queue:
            self.task_queue.append(task_id)
        
        # Remove from old agent
        if old_agent_id in self.agents:
            old_agent = self.agents[old_agent_id]
            if task_id in old_agent.current_tasks:
                old_agent.current_tasks.remove(task_id)
                old_agent.status = "available" if len(old_agent.current_tasks) < old_agent.max_concurrent_tasks else "busy"
        
        logger.info(f"Task {task.name} reassigned from agent {old_agent_id}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        async with self.lock:
            total_tasks = len(self.tasks)
            pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
            in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
            completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
            active_agents = len([a for a in self.agents.values() if a.status != "offline"])
            
            return {
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completed_tasks": completed_tasks,
                "active_agents": active_agents,
                "total_agents": len(self.agents),
                "queue_length": len(self.task_queue)
            }
    
    async def heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat"""
        async with self.lock:
            if agent_id not in self.agents:
                return False
            
            self.agents[agent_id].last_heartbeat = datetime.now()
            return True
    
    async def cleanup_inactive_agents(self, timeout_seconds: int = 300):
        """Remove agents that haven't sent heartbeat in specified time"""
        async with self.lock:
            current_time = datetime.now()
            inactive_agents = []
            
            for agent_id, agent in self.agents.items():
                if (current_time - agent.last_heartbeat).total_seconds() > timeout_seconds:
                    inactive_agents.append(agent_id)
            
            for agent_id in inactive_agents:
                await self.unregister_agent(agent_id)
                logger.warning(f"Removed inactive agent: {agent_id}")


class MCPClient:
    """Client for agents to interact with the MCP system"""
    
    def __init__(self, server_url: str, agent_id: str, agent_name: str, capabilities: List[str]):
        self.server_url = server_url
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.session = None
        self.heartbeat_task = None
    
    async def connect(self):
        """Connect to the MCP server"""
        self.session = aiohttp.ClientSession()
        
        # Register with server
        success = await self.register()
        if success:
            # Start heartbeat
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info(f"Agent {self.agent_name} connected to MCP server")
        else:
            logger.error(f"Failed to connect agent {self.agent_name} to MCP server")
        
        return success
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        if self.session:
            await self.session.close()
        
        logger.info(f"Agent {self.agent_name} disconnected from MCP server")
    
    async def register(self) -> bool:
        """Register with the MCP server"""
        try:
            async with self.session.post(f"{self.server_url}/register", json={
                "agent_id": self.agent_id,
                "name": self.agent_name,
                "capabilities": self.capabilities,
                "max_concurrent_tasks": 3
            }) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
    
    async def get_available_tasks(self) -> List[Dict[str, Any]]:
        """Get available tasks for this agent"""
        try:
            async with self.session.get(f"{self.server_url}/tasks/available/{self.agent_id}") as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logger.error(f"Failed to get available tasks: {e}")
            return []
    
    async def claim_task(self, task_id: str) -> bool:
        """Claim a task for execution"""
        try:
            async with self.session.post(f"{self.server_url}/tasks/claim", json={
                "agent_id": self.agent_id,
                "task_id": task_id
            }) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to claim task: {e}")
            return False
    
    async def complete_task(self, task_id: str, result: Dict[str, Any] = None, 
                          duration_seconds: float = None) -> bool:
        """Mark a task as completed"""
        try:
            payload = {
                "agent_id": self.agent_id,
                "task_id": task_id
            }
            if result:
                payload["result"] = result
            if duration_seconds:
                payload["actual_duration"] = duration_seconds
            
            async with self.session.post(f"{self.server_url}/tasks/complete", json=payload) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to the server"""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                async with self.session.post(f"{self.server_url}/heartbeat", json={
                    "agent_id": self.agent_id
                }) as response:
                    if response.status != 200:
                        logger.warning("Heartbeat failed, attempting to reconnect...")
                        await self.register()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")


# Global MCP server instance
mcp_server = MCPServer()

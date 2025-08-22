"""
MCP Client - Interface for agents to interact with the MCP system
Enhanced with Status Tracking and Overlap Prevention
"""

import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MCPClient:
    """Client interface for agents to interact with the MCP system"""
    
    def __init__(self, agent_name: str, capabilities: List[str]):
        self.agent_id = str(uuid.uuid4())
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.current_tasks: List[str] = []
        self.is_registered = False
        self.task_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0
        }
    
    async def register_with_server(self, server) -> bool:
        """Register this agent with the MCP server"""
        try:
            success = await server.register_agent(
                self.agent_id, 
                self.agent_name, 
                self.capabilities
            )
            self.is_registered = success
            if success:
                logger.info(f"Agent {self.agent_name} registered successfully with capabilities: {self.capabilities}")
            return success
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return False
    
    async def get_available_tasks(self, server) -> List[Any]:
        """Get available tasks from the server"""
        if not self.is_registered:
            logger.warning("Agent not registered with server")
            return []
        
        try:
            tasks = await server.get_available_tasks(self.agent_id)
            logger.info(f"Retrieved {len(tasks)} available tasks for {self.agent_name}")
            return tasks
        except Exception as e:
            logger.error(f"Failed to get available tasks: {e}")
            return []
    
    async def claim_task(self, server, task_id: str) -> bool:
        """Claim a task for execution"""
        if not self.is_registered:
            logger.warning("Agent not registered with server")
            return False
        
        try:
            success = await server.claim_task(self.agent_id, task_id)
            if success:
                self.current_tasks.append(task_id)
                logger.info(f"Task {task_id} claimed by {self.agent_name}")
                
                # Log task claim for overlap prevention
                self._log_task_action("claimed", task_id, server)
            return success
        except Exception as e:
            logger.error(f"Failed to claim task: {e}")
            return False
    
    async def complete_task(self, server, task_id: str, result: Dict[str, Any] = None, 
                          execution_time: float = None) -> bool:
        """Mark a task as completed"""
        if task_id not in self.current_tasks:
            logger.warning(f"Task {task_id} not in current tasks")
            return False
        
        try:
            # Update task status in server
            if hasattr(server, 'complete_task'):
                await server.complete_task(self.agent_id, task_id, result)
            
            # Remove from current tasks
            self.current_tasks.remove(task_id)
            
            # Update performance metrics
            if execution_time:
                self._update_performance_metrics(execution_time, success=True)
            
            # Log task completion
            self._log_task_action("completed", task_id, server, result, execution_time)
            
            logger.info(f"Task {task_id} completed by {self.agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    async def fail_task(self, server, task_id: str, error: str = None, execution_time: float = None) -> bool:
        """Mark a task as failed"""
        if task_id not in self.current_tasks:
            logger.warning(f"Task {task_id} not in current tasks")
            return False
        
        try:
            # Update task status in server
            if hasattr(server, 'fail_task'):
                await server.fail_task(self.agent_id, task_id, error)
            
            # Remove from current tasks
            self.current_tasks.remove(task_id)
            
            # Update performance metrics
            if execution_time:
                self._update_performance_metrics(execution_time, success=False)
            
            # Log task failure
            self._log_task_action("failed", task_id, server, {"error": error}, execution_time)
            
            logger.error(f"Task {task_id} failed by {self.agent_name}: {error}")
            return True
        except Exception as e:
            logger.error(f"Failed to mark task as failed: {e}")
            return False
    
    async def update_task_progress(self, server, task_id: str, progress: float, status_update: str = None) -> bool:
        """Update task progress"""
        if task_id not in self.current_tasks:
            logger.warning(f"Task {task_id} not in current tasks")
            return False
        
        try:
            # Update progress in server if supported
            if hasattr(server, 'update_task_progress'):
                await server.update_task_progress(task_id, progress, status_update)
            
            # Log progress update
            self._log_task_action("progress_update", task_id, server, {
                "progress": progress,
                "status_update": status_update
            })
            
            logger.info(f"Task {task_id} progress updated: {progress:.1%}")
            return True
        except Exception as e:
            logger.error(f"Failed to update task progress: {e}")
            return False
    
    def _log_task_action(self, action: str, task_id: str, server, data: Dict[str, Any] = None, 
                        execution_time: float = None):
        """Log task actions for audit and overlap prevention"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "action": action,
            "task_id": task_id,
            "data": data or {},
            "execution_time": execution_time
        }
        
        self.task_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]
        
        # Log to system logger
        logger.info(f"Task action logged: {action} on {task_id} by {self.agent_name}")
    
    def _update_performance_metrics(self, execution_time: float, success: bool):
        """Update agent performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
        
        self.performance_metrics["total_execution_time"] += execution_time
        
        # Calculate average execution time
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        if total_tasks > 0:
            self.performance_metrics["average_execution_time"] = (
                self.performance_metrics["total_execution_time"] / total_tasks
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.agent_name,
            "capabilities": self.capabilities,
            "current_tasks": self.current_tasks,
            "is_registered": self.is_registered,
            "task_count": len(self.current_tasks),
            "performance_metrics": self.performance_metrics,
            "task_history_count": len(self.task_history)
        }
    
    def get_task_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent task history"""
        return self.task_history[-limit:] if limit > 0 else self.task_history
    
    def export_task_logs(self, filepath: str = None) -> str:
        """Export task logs to file"""
        if not filepath:
            filepath = f"agent_{self.agent_name}_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "agent_info": {
                        "name": self.agent_name,
                        "id": self.agent_id,
                        "capabilities": self.capabilities
                    },
                    "performance_metrics": self.performance_metrics,
                    "task_history": self.task_history
                }, f, indent=2)
            
            logger.info(f"Task logs exported to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export task logs: {e}")
            return ""


class AgentBase:
    """Base class for all agents using the MCP system"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.mcp_client = MCPClient(name, capabilities)
        self.name = name
        self.capabilities = capabilities
        self.task_execution_times: Dict[str, float] = {}
    
    async def initialize(self, server) -> bool:
        """Initialize the agent with the MCP server"""
        return await self.mcp_client.register_with_server(server)
    
    async def process_tasks(self, server):
        """Main task processing loop for the agent"""
        while True:
            try:
                # Get available tasks
                available_tasks = await self.mcp_client.get_available_tasks(server)
                
                for task in available_tasks:
                    # Check if we can handle this task
                    if self._can_handle_task(task):
                        # Check for overlap prevention
                        if await self._check_task_overlap(server, task):
                            continue
                        
                        # Claim the task
                        if await self.mcp_client.claim_task(server, task.id):
                            # Execute the task
                            start_time = asyncio.get_event_loop().time()
                            result = await self._execute_task(task)
                            execution_time = asyncio.get_event_loop().time() - start_time
                            
                            # Store execution time
                            self.task_execution_times[task.id] = execution_time
                            
                            # Complete the task
                            if result.get("status") == "completed":
                                await self.mcp_client.complete_task(server, task.id, result, execution_time)
                            else:
                                await self.mcp_client.fail_task(server, task.id, result.get("error"), execution_time)
                
                # Wait before checking again
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(10)
    
    async def _check_task_overlap(self, server, task) -> bool:
        """Check if task is already being implemented by another agent"""
        try:
            # Get task status from server
            if hasattr(server, 'get_task_status'):
                task_status = await server.get_task_status(task.id)
                if task_status and task_status.get("agent_id") and task_status.get("agent_id") != self.mcp_client.agent_id:
                    logger.info(f"Task {task.name} already claimed by another agent, skipping")
                    return True
        except Exception as e:
            logger.warning(f"Could not check task overlap: {e}")
        
        return False
    
    def _can_handle_task(self, task) -> bool:
        """Check if this agent can handle a specific task"""
        # Override in subclasses for specific logic
        return True
    
    async def _execute_task(self, task):
        """Execute a specific task"""
        # Override in subclasses for specific task execution
        logger.info(f"Executing task: {task.name}")
        return {"status": "completed", "result": "default_result"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "capabilities": self.capabilities,
            "mcp_status": self.mcp_client.get_status(),
            "task_execution_times": self.task_execution_times
        }
    
    def export_logs(self, filepath: str = None) -> str:
        """Export agent logs"""
        return self.mcp_client.export_task_logs(filepath)

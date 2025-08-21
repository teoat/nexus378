"""
MCP Client - Interface for agents to interact with the MCP system
"""

import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPClient:
    """Client interface for agents to interact with the MCP system"""
    
    def __init__(self, agent_name: str, capabilities: List[str]):
        self.agent_id = str(uuid.uuid4())
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.current_tasks: List[str] = []
        self.is_registered = False
    
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
                logger.info(f"Agent {self.agent_name} registered successfully")
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
            return success
        except Exception as e:
            logger.error(f"Failed to claim task: {e}")
            return False
    
    async def complete_task(self, server, task_id: str, result: Dict[str, Any] = None) -> bool:
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
            logger.info(f"Task {task_id} completed by {self.agent_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.agent_name,
            "capabilities": self.capabilities,
            "current_tasks": self.current_tasks,
            "is_registered": self.is_registered,
            "task_count": len(self.current_tasks)
        }


class AgentBase:
    """Base class for all agents using the MCP system"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.mcp_client = MCPClient(name, capabilities)
        self.name = name
        self.capabilities = capabilities
    
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
                        # Claim the task
                        if await self.mcp_client.claim_task(server, task.id):
                            # Execute the task
                            result = await self._execute_task(task)
                            # Complete the task
                            await self.mcp_client.complete_task(server, task.id, result)
                
                # Wait before checking again
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(10)
    
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
            "mcp_status": self.mcp_client.get_status()
        }

"""
MCP Integration - Connects workflow orchestrator with MCP system
"""

import asyncio
import logging
from typing import Dict, List, Any
from .mcp_server import mcp_server
from .mcp_client import AgentBase

logger = logging.getLogger(__name__)


class MCPWorkflowIntegration:
    """Integrates MCP system with workflow orchestrator"""
    
    def __init__(self):
        self.agents: Dict[str, AgentBase] = {}
        self.task_mapping: Dict[str, str] = {}  # workflow_task_id -> mcp_task_id
    
    async def register_workflow_task(self, name: str, description: str, 
                                   dependencies: List[str] = None) -> str:
        """Register a workflow task with the MCP system"""
        try:
            task_id = await mcp_server.submit_task(name, description, dependencies)
            if task_id:
                logger.info(f"Workflow task registered with MCP: {name}")
                return task_id
            else:
                logger.warning(f"Failed to register workflow task: {name}")
                return None
        except Exception as e:
            logger.error(f"Error registering workflow task: {e}")
            return None
    
    async def create_agent(self, name: str, capabilities: List[str]) -> AgentBase:
        """Create and register a new agent"""
        agent = AgentBase(name, capabilities)
        success = await agent.initialize(mcp_server)
        
        if success:
            self.agents[name] = agent
            logger.info(f"Agent created and registered: {name}")
            return agent
        else:
            logger.error(f"Failed to create agent: {name}")
            return None
    
    async def start_agent_processing(self, agent_name: str):
        """Start task processing for an agent"""
        if agent_name not in self.agents:
            logger.error(f"Agent not found: {agent_name}")
            return
        
        agent = self.agents[agent_name]
        asyncio.create_task(agent.process_tasks(mcp_server))
        logger.info(f"Started task processing for agent: {agent_name}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "agents": {name: agent.get_status() for name, agent in self.agents.items()},
            "mcp_server": mcp_server.get_system_status() if hasattr(mcp_server, 'get_system_status') else {},
            "total_agents": len(self.agents)
        }


# Global integration instance
mcp_integration = MCPWorkflowIntegration()

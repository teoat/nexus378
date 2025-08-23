"""
Example Agent Implementation - Demonstrates MCP system usage
"""

import logging
from typing import Any, Dict

import asyncio

from .mcp_client import AgentBase
from .simple_registry import task_registry

logger = logging.getLogger(__name__)


class ForensicAnalysisAgent(AgentBase):
    """Example forensic analysis agent"""

    def __init__(self):
        capabilities = [
            "file_analysis",
            "memory_analysis",
            "network_analysis",
            "timeline_analysis",
        ]
        super().__init__("ForensicAnalysisAgent", capabilities)

    def _can_handle_task(self, task) -> bool:
        """Check if this agent can handle a specific task"""
        # Check if task requires forensic analysis capabilities
        required_capabilities = task.metadata.get("required_capabilities", [])
        if required_capabilities:
            return any(cap in self.capabilities for cap in required_capabilities)

        # Default to true for forensic-related tasks
        forensic_keywords = ["forensic", "analysis", "investigation", "evidence"]
        return any(
            keyword in task.name.lower() or keyword in task.description.lower()
            for keyword in forensic_keywords
        )

    async def _execute_task(self, task):
        """Execute a forensic analysis task"""
        logger.info(f"Executing forensic task: {task.name}")

        # Check if task is already implemented
        if task_registry.is_task_implemented(task.name, task.description):
            existing_agent = task_registry.get_implementing_agent(
                task.name, task.description
            )
            logger.warning(f"Task {task.name} already implemented by {existing_agent}")
            return {"status": "skipped", "reason": "already_implemented"}

        # Register task implementation
        task_registry.register_task(task.name, task.description, self.agent_id)

        # Simulate task execution
        await asyncio.sleep(2)  # Simulate processing time

        # Return task results
        result = {
            "status": "completed",
            "agent_id": self.agent_id,
            "task_name": task.name,
            "result": f"Forensic analysis completed for {task.name}",
            "timestamp": asyncio.get_event_loop().time(),
        }

        logger.info(f"Task {task.name} completed successfully")
        return result


class DataProcessingAgent(AgentBase):
    """Example data processing agent"""

    def __init__(self):
        capabilities = [
            "data_cleaning",
            "data_transformation",
            "data_validation",
            "report_generation",
        ]
        super().__init__("DataProcessingAgent", capabilities)

    def _can_handle_task(self, task) -> bool:
        """Check if this agent can handle data processing tasks"""
        data_keywords = ["data", "process", "clean", "transform", "validate", "report"]
        return any(
            keyword in task.name.lower() or keyword in task.description.lower()
            for keyword in data_keywords
        )

    async def _execute_task(self, task):
        """Execute a data processing task"""
        logger.info(f"Executing data processing task: {task.name}")

        # Check for duplicates
        if task_registry.is_task_implemented(task.name, task.description):
            existing_agent = task_registry.get_implementing_agent(
                task.name, task.description
            )
            logger.warning(f"Task {task.name} already implemented by {existing_agent}")
            return {"status": "skipped", "reason": "already_implemented"}

        # Register implementation
        task_registry.register_task(task.name, task.description, self.agent_id)

        # Simulate processing
        await asyncio.sleep(1.5)

        result = {
            "status": "completed",
            "agent_id": self.agent_id,
            "task_name": task.name,
            "result": f"Data processing completed for {task.name}",
            "timestamp": asyncio.get_event_loop().time(),
        }

        logger.info(f"Task {task.name} completed successfully")
        return result


async def create_example_agents(mcp_integration):
    """Create and start example agents"""
    # Create forensic analysis agent
    forensic_agent = await mcp_integration.create_agent(
        "ForensicAnalysisAgent",
        ["file_analysis", "memory_analysis", "network_analysis", "timeline_analysis"],
    )

    if forensic_agent:
        await mcp_integration.start_agent_processing("ForensicAnalysisAgent")

    # Create data processing agent
    data_agent = await mcp_integration.create_agent(
        "DataProcessingAgent",
        [
            "data_cleaning",
            "data_transformation",
            "data_validation",
            "report_generation",
        ],
    )

    if data_agent:
        await mcp_integration.start_agent_processing("DataProcessingAgent")

    return forensic_agent, data_agent

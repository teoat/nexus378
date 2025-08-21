#!/usr/bin/env python3
"""
Test Updated MCP Server - Verify the updated priority TODO list and functionality
"""

import asyncio
import logging

# Import the MCP server
from core.mcp_server import mcp_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_updated_mcp():
    """Test the updated MCP server functionality"""
    logger.info("🧪 Testing Updated MCP Server")
    
    # Get system status
    status = await mcp_server.get_system_status()
    logger.info(f"System Status: {status}")
    
    # Get priority TODO summary
    try:
        priority_summary = await mcp_server.get_priority_todo_summary()
        logger.info(f"Priority TODO Summary: {priority_summary}")
        
        # Show individual tasks
        logger.info("\n📋 Current Priority TODO Items:")
        for task in priority_summary.get("tasks", []):
            logger.info(f"  • {task['name']}")
            logger.info(f"    Priority: {task['priority']}")
            logger.info(f"    Duration: {task['estimated_duration']}")
            logger.info(f"    Status: {task['status']}")
            logger.info("")
            
    except Exception as e:
        logger.error(f"Error getting priority summary: {e}")
    
    # Show all tasks
    logger.info("\n🔍 All Tasks in MCP Server:")
    for task_id, task in mcp_server.tasks.items():
        logger.info(f"  Task: {task.name}")
        logger.info(f"    ID: {task.id}")
        logger.info(f"    Status: {task.status.value}")
        logger.info(f"    Priority: {task.priority.value}")
        logger.info(f"    Required Capabilities: {task.required_capabilities}")
        logger.info("")
    
    logger.info("✅ MCP Server Test Completed!")


async def main():
    """Main function"""
    await test_updated_mcp()


if __name__ == "__main__":
    asyncio.run(main())

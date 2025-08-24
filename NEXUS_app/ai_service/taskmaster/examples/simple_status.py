#!/usr/bin/env python3
Simple Status Update - Basic status monitoring for MCP Server

import asyncio
import logging

# Import the MCP server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def show_current_status():

    logger.info("📊 Current MCP Server Status")

    # Get system status
    status = await mcp_server.get_system_status()
    logger.info(f"System Status: {status}")

    # Get priority TODO summary
    try:
        priority_summary = await mcp_server.get_priority_todo_summary()
        logger.info(f"Priority TODO Summary: {priority_summary}")
    except Exception as e:
        logger.error(f"Error getting priority summary: {e}")

    # Show task details
    logger.info("\n📋 Task Details:")
    for task_id, task in mcp_server.tasks.items():
        logger.info(f"  Task: {task.name}")
        logger.info(f"    Status: {task.status.value}")
        logger.info(f"    Priority: {task.priority.value}")
        logger.info(f"    Assigned to: {task.agent_id or 'Unassigned'}")
        logger.info(f"    Progress: {getattr(task, 'progress', 0.0):.1%}")
        logger.info("")

async def main():

if __name__ == "__main__":
    asyncio.run(main())

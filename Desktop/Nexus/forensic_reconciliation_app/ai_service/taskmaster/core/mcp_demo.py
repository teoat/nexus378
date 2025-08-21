"""
MCP System Demo - Demonstrates the complete MCP system
"""

import asyncio
import logging
from typing import List
from .mcp_integration import mcp_integration
from .example_agent import create_example_agents
from .simple_registry import task_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_mcp_system():
    """Demonstrate the MCP system functionality"""
    logger.info("Starting MCP System Demo")
    
    # Create and start agents
    logger.info("Creating agents...")
    forensic_agent, data_agent = await create_example_agents(mcp_integration)
    
    if not forensic_agent or not data_agent:
        logger.error("Failed to create agents")
        return
    
    # Wait a moment for agents to initialize
    await asyncio.sleep(2)
    
    # Submit some example tasks
    logger.info("Submitting example tasks...")
    
    # Task 1: Forensic analysis
    task1_id = await mcp_integration.register_workflow_task(
        "Analyze Memory Dump",
        "Perform memory analysis on forensic memory dump file",
        dependencies=[]
    )
    
    # Task 2: Data processing (depends on Task 1)
    task2_id = await mcp_integration.register_workflow_task(
        "Process Analysis Results",
        "Clean and transform forensic analysis results",
        dependencies=[task1_id] if task1_id else []
    )
    
    # Task 3: Another forensic task
    task3_id = await mcp_integration.register_workflow_task(
        "Network Traffic Analysis",
        "Analyze network traffic patterns from pcap files",
        dependencies=[]
    )
    
    # Task 4: Duplicate task (should be detected)
    task4_id = await mcp_integration.register_workflow_task(
        "Analyze Memory Dump",
        "Perform memory analysis on forensic memory dump file",
        dependencies=[]
    )
    
    if task4_id is None:
        logger.info("✓ Duplicate task detection working correctly")
    
    # Wait for tasks to be processed
    logger.info("Waiting for tasks to be processed...")
    await asyncio.sleep(10)
    
    # Show system status
    logger.info("System Status:")
    status = mcp_integration.get_system_status()
    for key, value in status.items():
        if key == "agents":
            logger.info(f"  {key}:")
            for agent_name, agent_status in value.items():
                logger.info(f"    {agent_name}: {agent_status['mcp_status']['task_count']} tasks")
        else:
            logger.info(f"  {key}: {value}")
    
    # Show task registry status
    logger.info("Task Registry Status:")
    registry_summary = {
        "registered_tasks": len(task_registry.registered_tasks),
        "task_dependencies": len(task_registry.task_dependencies)
    }
    for key, value in registry_summary.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("Demo completed!")


async def demo_task_dependencies():
    """Demonstrate task dependency management"""
    logger.info("Demonstrating Task Dependencies...")
    
    # Clear existing tasks
    task_registry.registered_tasks.clear()
    task_registry.task_dependencies.clear()
    
    # Create dependent tasks
    task1 = "Data Collection"
    task2 = "Data Analysis"
    task3 = "Report Generation"
    
    # Add dependencies
    task_registry.add_dependency(task2, task1)  # Analysis depends on Collection
    task_registry.add_dependency(task3, task2)  # Report depends on Analysis
    
    # Check dependencies
    logger.info(f"Task '{task2}' dependencies: {task_registry.get_dependencies(task2)}")
    logger.info(f"Task '{task3}' dependencies: {task_registry.get_dependencies(task3)}")
    
    # Simulate task completion
    task_registry.register_task(task1, "Collect forensic data", "agent1")
    logger.info(f"Task '{task1}' completed")
    
    # Check if dependent tasks can proceed
    deps2 = task_registry.get_dependencies(task2)
    deps3 = task_registry.get_dependencies(task3)
    
    logger.info(f"Task '{task2}' can proceed: {len(deps2) == 0}")
    logger.info(f"Task '{task3}' can proceed: {len(deps3) == 0}")


async def main():
    """Main demo function"""
    try:
        # Run basic demo
        await demo_mcp_system()
        
        # Run dependency demo
        await demo_task_dependencies()
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

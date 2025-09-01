#!/usr/bin/env python3
MCP Server Demo - Demonstrates Task Assignment and Overlap Prevention

import asyncio
import logging
from datetime import datetime

# Import the MCP server

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DemoAgent:

            logger.info(f"✅ Agent {self.name} registered successfully")
        else:
            logger.error(f"❌ Failed to register agent {self.name}")
        return success

    async def claim_available_tasks(self) -> List[str]:

            logger.info(f"🔍 Agent {self.name} evaluating task: {task.name}")
            logger.info(f"   Priority: {task.priority.value}")
            logger.info(f"   Required Capabilities: {task.required_capabilities}")
            logger.info(f"   Agent Capabilities: {self.capabilities}")

            # Try to claim the task
            if await mcp_server.claim_task(self.agent_id, task.id):
                self.current_tasks.append(task.id)
                claimed_tasks.append(task.id)
                logger.info(f"✅ Agent {self.name} claimed task: {task.name}")
            else:
                logger.warning(
                    f"❌ Agent {self.name} failed to claim task: {task.name}"
                )

        return claimed_tasks

    async def work_on_tasks(self, work_duration: float = 2.0):

            logger.info(f"🤷 Agent {self.name} has no tasks to work on")
            return

        logger.info(
            f"🚧 Agent {self.name} working on {len(self.current_tasks)} tasks..."
        )
        await asyncio.sleep(work_duration)

        # Complete all tasks
        for task_id in self.current_tasks[
            :
        ]:  # Copy list to avoid modification during iteration
            await mcp_server.complete_task(
                self.agent_id,
                task_id,
                {
                    "completed_by": self.name,
                    "completion_time": datetime.now().isoformat(),
                    "result": "Task completed successfully",
                },
            )
            self.current_tasks.remove(task_id)
            logger.info(f"✅ Agent {self.name} completed task: {task_id}")

    async def heartbeat(self):

    logger.info("🚀 Starting MCP Server Demo")

    # Create demo agents with different capabilities
    agents = [
        DemoAgent(
            "agent_001",
            "Database Specialist",
            ["database_setup", "olap_configuration", "performance_optimization"],
        ),
        DemoAgent(
            "agent_002",
            "Security Expert",
            [
                "security",
                "authentication",
                "mfa_implementation",
                "encryption",
                "key_management",
            ],
        ),
        DemoAgent(
            "agent_003",
            "Python Developer",
            [
                "python_development",
                "algorithm_implementation",
                "load_balancing",
                "workflow_management",
                "dependency_resolution",
            ],
        ),
        DemoAgent(
            "agent_004",
            "ML Engineer",
            [
                "python_development",
                "machine_learning",
                "algorithm_implementation",
                "graph_algorithms",
                "fraud_detection",
            ],
        ),
        DemoAgent(
            "agent_005",
            "Compliance Specialist",
            ["python_development", "compliance", "risk_assessment"],
        ),
    ]

    # Register all agents
    logger.info("📝 Registering agents with MCP server...")
    for agent in agents:
        await agent.register()

    # Show initial system status
    status = await mcp_server.get_system_status()
    logger.info(f"📊 Initial System Status: {status}")

    # Round 1: Agents claim tasks
    logger.info("\n🔄 ROUND 1: Agents claiming tasks...")
    for agent in agents:
        claimed_tasks = await agent.claim_available_tasks()
        if claimed_tasks:
            logger.info(f"🎯 Agent {agent.name} claimed {len(claimed_tasks)} tasks")
        else:
            logger.info(f"😔 Agent {agent.name} couldn't claim any tasks")

    # Show status after claiming
    status = await mcp_server.get_system_status()
    logger.info(f"📊 Status after claiming: {status}")

    # Round 2: Agents work on tasks
    logger.info("\n🚧 ROUND 2: Agents working on tasks...")
    work_tasks = []
    for agent in agents:
        if agent.current_tasks:
            work_tasks.append(agent.work_on_tasks())

    if work_tasks:
        await asyncio.gather(*work_tasks)

    # Show final status
    status = await mcp_server.get_system_status()
    logger.info(f"📊 Final System Status: {status}")

    # Demonstrate overlap prevention
    logger.info("\n🛡️ DEMONSTRATING OVERLAP PREVENTION...")

    # Try to have multiple agents claim the same task (should fail)
    logger.info("🔒 Attempting to have multiple agents claim the same task...")

    # Create a new task
    task_id = await mcp_server.submit_task(
        name="Test Overlap Prevention",
        description="Testing that only one agent can claim a task",
        priority=TaskPriority.NORMAL,
        required_capabilities=["python_development"],
        estimated_duration="1 hour",
    )

    if task_id:
        # First agent claims it
        agent1_claimed = await mcp_server.claim_task("agent_003", task_id)
        logger.info(f"Agent 003 claim result: {agent1_claimed}")

        # Second agent tries to claim the same task (should fail)
        agent2_claimed = await mcp_server.claim_task("agent_004", task_id)
        logger.info(f"Agent 004 claim result: {agent2_claimed}")

        # Show task status
        task_status = await mcp_server.get_task_status(task_id)
        logger.info(f"Task status: {task_status}")

    logger.info("\n🎉 MCP Server Demo Completed!")

async def show_task_details():

    logger.info("\n📋 DETAILED TASK INFORMATION:")

    # Get all tasks from the MCP server
    for task_id, task in mcp_server.tasks.items():
        logger.info(f"\n🔍 Task: {task.name}")
        logger.info(f"   ID: {task.id}")
        logger.info(f"   Status: {task.status.value}")
        logger.info(f"   Priority: {task.status.value}")
        logger.info(f"   Assigned to: {task.agent_id or 'Unassigned'}")
        logger.info(f"   Required Capabilities: {task.required_capabilities}")
        logger.info(f"   Estimated Duration: {task.estimated_duration}")
        logger.info(f"   Created: {task.created_at}")

async def main():

        logger.error(f"❌ Demo failed with error: {e}")
        raise

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())

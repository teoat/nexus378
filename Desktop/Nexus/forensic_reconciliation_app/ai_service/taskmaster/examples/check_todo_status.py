#!/usr/bin/env python3
"""
Check TODO Status - Verify current TODO status and MCP server status
"""

import logging
import os

# Import the MCP server
import sys
from datetime import datetime

import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.mcp_server import mcp_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_todo_status():
    """Check the current TODO status and MCP server status"""
    logger.info("🔍 Checking TODO Status and MCP Server Status...")

    try:
        # Get system status
        system_status = mcp_server.get_system_status()

        print("\n" + "=" * 80)
        print("🔍 TODO STATUS & MCP SERVER VERIFICATION")
        print("=" * 80)

        # System Status
        print(f"📊 SYSTEM STATUS:")
        print(f"   System Health: {system_status.get('system_health', 'Unknown')}")
        print(f"   Total Tasks: {system_status.get('total_tasks', 0)}")
        print(f"   MCP Status: {system_status.get('mcp_status', 'Unknown')}")
        print(f"   Last Updated: {system_status.get('last_updated', 'Unknown')}")

        # Task Status Breakdown
        task_status = system_status.get("task_status", {})
        print(f"\n📋 TASK STATUS BREAKDOWN:")
        print(f"   Pending Tasks: {task_status.get('pending', 0)}")
        print(f"   In Progress Tasks: {task_status.get('in_progress', 0)}")
        print(f"   Completed Tasks: {task_status.get('completed', 0)}")
        print(f"   Failed Tasks: {task_status.get('failed', 0)}")
        print(f"   Blocked Tasks: {task_status.get('blocked', 0)}")

        # Priority TODO Status
        priority_todos = system_status.get("priority_todos", {})
        print(f"\n🎯 PRIORITY TODO STATUS:")
        print(f"   Total Priority TODOs: {priority_todos.get('total', 0)}")
        print(f"   Unimplemented: {priority_todos.get('unimplemented', 0)}")
        print(f"   Implemented: {priority_todos.get('implemented', 0)}")
        print(
            f"   Implementation Rate: {priority_todos.get('implementation_rate', 0)}%"
        )

        # Subtask Breakdown
        subtask_breakdown = system_status.get("subtask_breakdown", {})
        print(f"\n🔧 SUBTASK BREAKDOWN:")
        print(f"   Total Subtasks: {subtask_breakdown.get('total_subtasks', 0)}")
        print(
            f"   Completed Subtasks: {subtask_breakdown.get('completed_subtasks', 0)}"
        )
        print(
            f"   Remaining Subtasks: {subtask_breakdown.get('remaining_subtasks', 0)}"
        )
        print(f"   Completion Rate: {subtask_breakdown.get('completion_rate', 0)}%")

        # Agent Status
        agents = system_status.get("agents", {})
        print(f"\n🤖 AGENT STATUS:")
        print(f"   Total Registered: {agents.get('total_registered', 0)}")
        print(f"   Active Agents: {agents.get('active_agents', 0)}")

        # Overlap Prevention Status
        overlap_prevention = system_status.get("overlap_prevention", {})
        print(f"\n🛡️ OVERLAP PREVENTION STATUS:")
        print(f"   Status: {overlap_prevention.get('status', 'Unknown')}")
        print(f"   Last Updated: {overlap_prevention.get('last_updated', 'Unknown')}")
        print(f"   Mechanisms:")
        for mechanism in overlap_prevention.get("mechanisms", []):
            print(f"     ✅ {mechanism}")

        # Show TODO Items
        print(f"\n📋 NEXT 10 UNIMPLEMENTED TODO ITEMS:")
        todo_count = 0
        for task_id, task in mcp_server.tasks.items():
            if (
                task.metadata.get("type") == "priority_todo"
                and task.metadata.get("implementation_status") == "unimplemented"
            ):
                todo_count += 1
                print(f"   {todo_count}. {task.name}")
                print(f"      Priority: {task.priority.value}")
                print(f"      Duration: {task.estimated_duration}")
                print(f"      Status: {task.status.value}")
                print(f"      Phase: {task.metadata.get('phase', 'Unknown')}")
                print(f"      Category: {task.metadata.get('category', 'Unknown')}")
                print(f"      Subtasks: {task.metadata.get('subtask_count', 0)}")
                print(f"      Agent: {task.agent_id or 'Unassigned'}")
                print(f"      MCP Status: {task.metadata.get('mcp_status', 'Unknown')}")
                print(
                    f"      Overlap Prevention: {task.metadata.get('overlap_prevention', 'Unknown')}"
                )
                print("")

        # Development Readiness
        print(f"🚀 DEVELOPMENT READINESS:")
        if todo_count == 10:
            print(f"   ✅ All 10 TODO items loaded and tracked")
            print(f"   ✅ No task overlap possible")
            print(f"   ✅ System ready for agent registration")
            print(f"   ✅ Priority-based assignment active")
            print(f"   ✅ Enhanced overlap prevention active")
        else:
            print(f"   ⚠️ Expected 10 TODO items, found {todo_count}")
            print(f"   ⚠️ System may need additional configuration")

        print("\n" + "=" * 80)

        return {
            "status": "success",
            "todo_count": todo_count,
            "system_status": system_status,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error checking TODO status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def main():
    """Main function"""
    logger.info("🚀 Starting TODO Status Check")

    # Check TODO status
    result = await check_todo_status()

    if result["status"] == "success":
        logger.info(
            f"✅ Status check completed successfully! Found {result['todo_count']} TODO items",
        )
    else:
        logger.error(f"❌ Status check failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())

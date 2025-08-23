#!/usr/bin/env python3
"""
Status Monitor - Comprehensive monitoring and status updates for MCP Server and TODO tracking
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import asyncio

# Import the MCP server
from core.mcp_server import TaskPriority, TaskStatus, mcp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StatusMonitor:
    """Comprehensive status monitoring for MCP Server and TODO tracking"""

    def __init__(self):
        self.mcp_server = mcp_server

    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the entire system"""
        try:
            # Get system status
            system_status = await self.mcp_server.get_system_status()

            # Get priority TODO summary
            priority_summary = await self.mcp_server.get_priority_todo_summary()

            # Get agent information
            agent_info = await self._get_agent_summary()

            return {
                "timestamp": datetime.now().isoformat(),
                "system_status": system_status,
                "priority_todos": priority_summary,
                "agents": agent_info,
                "overall_health": self._calculate_health_score(
                    system_status, priority_summary
                ),
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
            return {"error": str(e)}

    async def _get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of all registered agents"""
        agents = {}

        for agent_id, agent in self.mcp_server.agents.items():
            workload = await self.mcp_server.get_agent_workload(agent_id)
            agents[agent_id] = workload

        return agents

    def _calculate_health_score(
        self, system_status: Dict[str, Any], priority_summary: Dict[str, Any]
    ):
        """Calculate overall system health score"""
        try:
            # Calculate completion rate
            total_tasks = priority_summary.get("total_tasks", 0)
            completed_tasks = priority_summary.get("by_status", {}).get("completed", 0)
            completion_rate = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            )

            # Calculate progress rate
            in_progress = priority_summary.get("by_status", {}).get("in_progress", 0)
            progress_rate = (
                ((completed_tasks + in_progress) / total_tasks * 100)
                if total_tasks > 0
                else 0
            )

            # Calculate health score (0-100)
            health_score = min(100, completion_rate + (progress_rate * 0.5))

            # Determine health status
            if health_score >= 80:
                health_status = "EXCELLENT"
            elif health_score >= 60:
                health_status = "GOOD"
            elif health_score >= 40:
                health_status = "FAIR"
            elif health_score >= 20:
                health_status = "POOR"
            else:
                health_status = "CRITICAL"

            return {
                "score": round(health_score, 1),
                "status": health_status,
                "completion_rate": round(completion_rate, 1),
                "progress_rate": round(progress_rate, 1),
                "metrics": {
                    "total_tasks": total_tasks,
                    "completed": completed_tasks,
                    "in_progress": in_progress,
                    "pending": priority_summary.get("by_status", {}).get("pending", 0),
                    "failed": priority_summary.get("by_status", {}).get("failed", 0),
                },
            }
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return {"score": 0, "status": "ERROR", "error": str(e)}

    async def refresh_priority_todos(self) -> bool:
        """Refresh the priority TODO list"""
        try:
            await self.mcp_server.refresh_priority_todos()
            logger.info("Priority TODO list refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Error refreshing priority todos: {e}")
            return False

    async def update_task_progress(
        self, task_id: str, progress: float, status_update: str = None
    ):
        """Update progress for a specific task"""
        try:
            success = await self.mcp_server.update_task_progress(
                task_id, progress, status_update
            )
            if success:
                logger.info(f"Task {task_id} progress updated to {progress:.1%}")
            return success
        except Exception as e:
            logger.error(f"Error updating task progress: {e}")
            return False

    async def get_task_details(self, task_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific task"""
        try:
            task_status = await self.mcp_server.get_task_status(task_id)
            if task_status:
                # Get additional details if task is assigned
                if task_status.get("agent_id"):
                    agent_workload = await self.mcp_server.get_agent_workload(
                        task_status["agent_id"]
                    )
                    task_status["agent_details"] = agent_workload

                return task_status
            return {}
        except Exception as e:
            logger.error(f"Error getting task details: {e}")
            return {"error": str(e)}

    async def get_phase_summary(self) -> Dict[str, Any]:
        """Get summary organized by development phases"""
        try:
            priority_summary = await self.mcp_server.get_priority_todo_summary()

            phase_summary = {}
            for task in priority_summary.get("tasks", []):
                phase = task.get("phase", "Unknown")
                if phase not in phase_summary:
                    phase_summary[phase] = {
                        "total_tasks": 0,
                        "completed": 0,
                        "in_progress": 0,
                        "pending": 0,
                        "failed": 0,
                        "estimated_hours": 0,
                        "tasks": [],
                    }

                phase_summary[phase]["total_tasks"] += 1
                phase_summary[phase]["tasks"].append(task)

                # Count by status
                status = task.get("status", "pending")
                if status == "completed":
                    phase_summary[phase]["completed"] += 1
                elif status == "in_progress":
                    phase_summary[phase]["in_progress"] += 1
                elif status == "failed":
                    phase_summary[phase]["failed"] += 1
                else:
                    phase_summary[phase]["pending"] += 1

                # Calculate estimated hours
                duration_str = task.get("estimated_duration", "0 hours")
                try:
                    hours = float(duration_str.split()[0])
                    phase_summary[phase]["estimated_hours"] += hours
                except (ValueError, IndexError):
                    pass

            return phase_summary
        except Exception as e:
            logger.error(f"Error getting phase summary: {e}")
            return {"error": str(e)}

    async def generate_status_report(self) -> str:
        """Generate a human-readable status report"""
        try:
            status = await self.get_comprehensive_status()

            report = []
            report.append("=" * 80)
            report.append("🔍 FORENSIC RECONCILIATION + FRAUD PLATFORM - STATUS REPORT")
            report.append("=" * 80)
            report.append(f"📅 Generated: {status['timestamp']}")
            report.append("")

            # System Health
            health = status.get("overall_health", {})
            report.append("🏥 SYSTEM HEALTH")
            report.append(
                f"   Overall Score: {health.get('score', 0)}/100 - {health.get('status', 'Unknown')}"
            )
            report.append(f"   Completion Rate: {health.get('completion_rate', 0)}%")
            report.append(f"   Progress Rate: {health.get('progress_rate', 0)}%")
            report.append("")

            # Priority TODO Summary
            todos = status.get("priority_todos", {})
            report.append("🎯 PRIORITY TODO SUMMARY")
            report.append(f"   Total Tasks: {todos.get('total_tasks', 0)}")
            report.append(
                f"   Critical: {todos.get('by_priority', {}).get('critical', 0)}"
            )
            report.append(f"   High: {todos.get('by_priority', {}).get('high', 0)}")
            report.append(f"   Normal: {todos.get('by_priority', {}).get('normal', 0)}")
            report.append("")

            # Phase Summary
            phase_summary = await self.get_phase_summary()
            report.append("📋 PHASE SUMMARY")
            for phase, data in phase_summary.items():
                if isinstance(data, dict) and "total_tasks" in data:
                    report.append(f"   {phase}:")
                    report.append(
                        f"     Tasks: {data['total_tasks']} | Completed: {data['completed']} | In Progress: {data['in_progress']} | Pending: {data['pending']}",
                    )
                    report.append(
                        f"     Estimated Hours: {data['estimated_hours']:.1f}",
                    )
            report.append("")

            # Agent Status
            agents = status.get("agents", {})
            if agents:
                report.append("🤖 AGENT STATUS")
                for agent_id, agent_data in agents.items():
                    if isinstance(agent_data, dict):
                        name = agent_data.get("name", "Unknown")
                        task_count = agent_data.get("task_count", 0)
                        status = agent_data.get("status", "Unknown")
                        report.append(
                            f"   {name} ({agent_id}): {task_count} tasks | Status: {status}"
                        )
                report.append("")

            # Recent Activity
            report.append("📊 RECENT ACTIVITY")
            system_status = status.get("system_status", {})
            report.append(f"   Tasks Pending: {system_status.get('pending_tasks', 0)}")
            report.append(
                f"   Tasks In Progress: {system_status.get('in_progress_tasks', 0)}"
            )
            report.append(
                f"   Tasks Completed: {system_status.get('completed_tasks', 0)}"
            )
            report.append(f"   Tasks Failed: {system_status.get('failed_tasks', 0)}")
            report.append(
                f"   Available Agents: {system_status.get('available_agents', 0)}"
            )
            report.append("")

            report.append("=" * 80)
            report.append("📝 End of Status Report")
            report.append("=" * 80)

            return "\n".join(report)
        except Exception as e:
            logger.error(f"Error generating status report: {e}")
            return f"Error generating status report: {e}"


async def main():
    """Main function to demonstrate status monitoring"""
    monitor = StatusMonitor()

    logger.info("🚀 Starting Status Monitor Demo")

    # Get comprehensive status
    logger.info("📊 Getting comprehensive status...")
    status = await monitor.get_comprehensive_status()
    logger.info(
        f"System Status: {status.get('overall_health', {}).get('status', 'Unknown')}"
    )

    # Generate status report
    logger.info("📋 Generating status report...")
    report = await monitor.generate_status_report()
    print(report)

    # Get phase summary
    logger.info("📋 Getting phase summary...")
    phase_summary = await monitor.get_phase_summary()
    logger.info(f"Phase Summary: {phase_summary}")

    logger.info("🎉 Status Monitor Demo Completed!")


if __name__ == "__main__":
    asyncio.run(main())

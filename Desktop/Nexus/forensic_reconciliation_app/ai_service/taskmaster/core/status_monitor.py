"""
Status Monitor - Comprehensive monitoring and logging for MCP system
Tracks TODO items and prevents overlapping implementations by agents
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncio

from .mcp_server import mcp_server
from .simple_registry import task_registry

logger = logging.getLogger(__name__)


class StatusMonitor:
    """Comprehensive status monitoring for MCP system"""

    def __init__(self):
        self.monitoring_active = False
        self.monitoring_interval = 30  # seconds
        self.status_history: List[Dict[str, Any]] = []
        self.overlap_alerts: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
<<<<<<< Updated upstream
        self.queue_metrics: Dict[str, Any] = {}
        
=======

>>>>>>> Stashed changes
    async def start_monitoring(self):
        """Start the status monitoring system"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        logger.info("Starting MCP status monitoring")

        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop the status monitoring system"""
        self.monitoring_active = False
        logger.info("Stopping MCP status monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system status
                await self._collect_system_status()

                # Check for overlaps
                await self._check_overlaps()

                # Update performance metrics
                await self._update_performance_metrics()

<<<<<<< Updated upstream
                # Collect queue metrics
                await self._collect_queue_metrics()
                
=======
>>>>>>> Stashed changes
                # Generate status report
                await self._generate_status_report()

                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    async def _collect_system_status(self):
        """Collect comprehensive system status"""
        try:
            # Get MCP server status
            mcp_status = await mcp_server.get_system_status()

            # Get task registry status
            registry_summary = task_registry.get_priority_todo_summary()

            # Get agent statuses
            agent_statuses = {}
            for agent_id, agent in mcp_server.agents.items():
                agent_statuses[agent_id] = {
                    "name": agent.name,
                    "status": agent.status,
                    "current_tasks": len(agent.current_tasks),
                    "capabilities": agent.capabilities,
                    "last_heartbeat": agent.last_heartbeat.isoformat(),
                }

            # Compile comprehensive status
            status_snapshot = {
                "timestamp": datetime.now().isoformat(),
                "mcp_server": mcp_status,
                "task_registry": registry_summary,
                "agents": agent_statuses,
                "overlap_alerts": len(self.overlap_alerts),
                "performance_metrics": self.performance_metrics,
<<<<<<< Updated upstream
                "queue_metrics": self.queue_metrics
=======
>>>>>>> Stashed changes
            }

            # Store in history
            self.status_history.append(status_snapshot)

            # Keep only last 1000 status snapshots
            if len(self.status_history) > 1000:
                self.status_history = self.status_history[-1000:]

            logger.debug(f"System status collected at {status_snapshot['timestamp']}")

        except Exception as e:
            logger.error(f"Error collecting system status: {e}")

    async def _check_overlaps(self):
        """Check for potential overlapping implementations"""
        try:
            current_overlaps = []

            # Check for duplicate task submissions
            task_names = {}
            for task_id, task in mcp_server.tasks.items():
                if task.status.value in ["pending", "in_progress"]:
                    task_key = f"{task.name.lower()}:{task.description.lower()}"
                    if task_key in task_names:
                        overlap_info = {
                            "type": "duplicate_task",
                            "severity": "high",
                            "timestamp": datetime.now().isoformat(),
                            "task1": {
                                "id": task_names[task_key],
                                "name": task.name,
                                "agent": mcp_server.tasks[
                                    task_names[task_key]
                                ].agent_id,
                            },
                            "task2": {
                                "id": task_id,
                                "name": task.name,
                                "agent": task.agent_id,
                            },
                            "description": f"Duplicate task detected: {task.name}",
                        }
                        current_overlaps.append(overlap_info)
                    else:
                        task_names[task_key] = task_id

            # Check for capability conflicts
            for agent_id, agent in mcp_server.agents.items():
                for other_agent_id, other_agent in mcp_server.agents.items():
                    if agent_id != other_agent_id:
                        # Check if agents have overlapping capabilities and are working on similar tasks
                        common_capabilities = set(agent.capabilities).intersection(
                            set(other_agent.capabilities)
                        )
                        if len(common_capabilities) > 0:
                            # Check if they're working on similar tasks
                            for task_id in agent.current_tasks:
                                if task_id in mcp_server.tasks:
                                    task = mcp_server.tasks[task_id]
                                    if any(
                                        cap in other_agent.capabilities
                                        for cap in task.required_capabilities
                                    ):
                                        overlap_info = {
                                            "type": "capability_conflict",
                                            "severity": "medium",
                                            "timestamp": datetime.now().isoformat(),
                                            "agent1": {
                                                "id": agent_id,
                                                "name": agent.name,
                                                "capabilities": agent.capabilities,
                                            },
                                            "agent2": {
                                                "id": other_agent_id,
                                                "name": other_agent.name,
                                                "capabilities": other_agent.capabilities,
                                            },
                                            "common_capabilities": list(
                                                common_capabilities
                                            ),
                                            "conflicting_task": task.name,
                                        }
                                        current_overlaps.append(overlap_info)

            # Update overlap alerts
            self.overlap_alerts = current_overlaps

            if current_overlaps:
                logger.warning(f"Detected {len(current_overlaps)} potential overlaps")

        except Exception as e:
            logger.error(f"Error checking overlaps: {e}")

    async def _update_performance_metrics(self):
        """Update system performance metrics"""
        try:
            # Calculate task completion rates
            total_tasks = len(mcp_server.tasks)
            completed_tasks = len(mcp_server.completed_tasks)
            failed_tasks = len(
                [t for t in mcp_server.tasks.values() if t.status.value == "failed"]
            )

            completion_rate = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            )
            failure_rate = (failed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # Calculate average task duration
            task_durations = []
            for task in mcp_server.tasks.values():
                if task.status.value == "completed" and "started_at" in task.metadata:
                    # This would need to be implemented in the Task class
                    pass

            # Update metrics
            self.performance_metrics.update(
                {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "failed_tasks": failed_tasks,
                    "completion_rate": round(completion_rate, 2),
                    "failure_rate": round(failure_rate, 2),
                    "active_agents": len(
                        [
                            a
                            for a in mcp_server.agents.values()
                            if a.status == "available"
                        ]
                    ),
                    "last_updated": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    async def _generate_status_report(self):
        """Generate comprehensive status report"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_health": self._assess_system_health(),
                "priority_todos": self._get_todo_status_summary(),
                "agent_workloads": self._get_agent_workload_summary(),
                "overlap_alerts": self.overlap_alerts,
                "recommendations": self._generate_recommendations(),
            }

            # Log report summary
            logger.info(
                f"Status report generated - Health: {report['system_health']}, "
                f"Todos: {report['priority_todos']['pending']} pending, "
                f"Overlaps: {len(report['overlap_alerts'])}"
            )

            return report

        except Exception as e:
            logger.error(f"Error generating status report: {e}")
            return {}

    def _assess_system_health(self) -> str:
        """Assess overall system health"""
        try:
            # Check for critical issues
            if len(self.overlap_alerts) > 5:
                return "critical"

            # Check completion rates
            if self.performance_metrics.get("completion_rate", 0) < 50:
                return "poor"

            if self.performance_metrics.get("completion_rate", 0) < 80:
                return "fair"

            return "good"

        except Exception:
            return "unknown"

    def _get_todo_status_summary(self) -> Dict[str, Any]:
        """Get summary of priority TODO status"""
        try:
            registry_summary = task_registry.get_priority_todo_summary()
            return {
                "total": registry_summary.get("total_todos", 0),
                "pending": registry_summary.get("by_status", {}).get("pending", 0),
                "in_progress": registry_summary.get("by_status", {}).get(
                    "in_progress", 0
                ),
                "completed": registry_summary.get("by_status", {}).get("completed", 0),
                "by_priority": registry_summary.get("by_priority", {}),
            }
        except Exception:
            return {
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "by_priority": {},
            }

    def _get_agent_workload_summary(self) -> Dict[str, Any]:
        """Get summary of agent workloads"""
        try:
            workloads = {}
            for agent_id, agent in mcp_server.agents.items():
                workloads[agent.name] = {
                    "current_tasks": len(agent.current_tasks),
                    "status": agent.status,
                    "capabilities": len(agent.capabilities),
                }
            return workloads
        except Exception:
            return {}

    def _generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []

        try:
            # Check for high overlap alerts
            if len(self.overlap_alerts) > 3:
                recommendations.append(
                    "High number of overlap alerts detected. Review agent assignments and task distribution.",
                )

            # Check for low completion rates
            if self.performance_metrics.get("completion_rate", 0) < 70:
                recommendations.append(
                    "Low task completion rate. Consider adding more agents or reviewing task complexity.",
                )

            # Check for agent availability
            available_agents = len(
                [a for a in mcp_server.agents.values() if a.status == "available"]
            )
            if available_agents == 0:
                recommendations.append(
                    "No available agents. Check agent health and restart if necessary.",
                )

            # Check for priority TODO distribution
            todo_summary = self._get_todo_status_summary()
            if todo_summary.get("pending", 0) > 5:
                recommendations.append(
                    "High number of pending priority TODOs. Consider agent capacity planning.",
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations due to system error"]

    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status"""
        if not self.status_history:
            return {"status": "no_data", "message": "No status data available"}

        return self.status_history[-1]

    def get_status_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get status history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_history = []
        for status in self.status_history:
            try:
                status_time = datetime.fromisoformat(status["timestamp"])
                if status_time >= cutoff_time:
                    filtered_history.append(status)
            except Exception:
                continue

        return filtered_history

    def export_status_report(self, filepath: str = None) -> str:
        """Export comprehensive status report to file"""
        if not filepath:
            filepath = (
                f"mcp_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "monitoring_config": {
                    "monitoring_active": self.monitoring_active,
                    "monitoring_interval": self.monitoring_interval,
                },
                "current_status": self.get_current_status(),
                "status_history": self.status_history[-100:],  # Last 100 entries
                "overlap_alerts": self.overlap_alerts,
                "performance_metrics": self.performance_metrics,
            }

            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Status report exported to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to export status report: {e}")
            return ""

    async def _collect_queue_metrics(self):
        """Placeholder for collecting queue metrics from RabbitMQ or other message brokers."""
        try:
            # In a real implementation, this would connect to RabbitMQ's management API
            # or use a client library to get queue stats.
            # For now, we'll simulate some metrics.
            import random
            queues = ["task_queue_high", "task_queue_medium", "task_queue_low", "dead_letter_queue"]

            queue_data = {}
            for queue_name in queues:
                queue_data[queue_name] = {
                    "messages_ready": random.randint(0, 1000),
                    "messages_unacknowledged": random.randint(0, 50),
                    "consumers": random.randint(1, 10),
                    "publish_rate": round(random.uniform(10, 100), 2),
                    "deliver_rate": round(random.uniform(10, 100), 2),
                }

            self.queue_metrics = {
                "provider": "RabbitMQ (simulated)",
                "queues": queue_data,
                "last_updated": datetime.now().isoformat()
            }
            logger.debug("Queue metrics collected.")

        except Exception as e:
            logger.error(f"Error collecting queue metrics: {e}")


# Global status monitor instance
status_monitor = StatusMonitor()

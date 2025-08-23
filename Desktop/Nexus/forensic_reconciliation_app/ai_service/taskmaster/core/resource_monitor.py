"""
Resource Monitor - System Health and Resource Monitoring

This module implements the ResourceMonitor class that provides comprehensive
monitoring of system resources, agent health, and performance metrics.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import asyncio
import psutil


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class SystemHealth:
    overall_status: HealthStatus
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: datetime


@dataclass
class ResourceUsage:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    timestamp: datetime


@dataclass
class AgentHealth:
    agent_id: str
    status: HealthStatus
    last_heartbeat: datetime
    response_time: float
    error_count: int
    performance_score: float


@dataclass
class Alert:
    alert_id: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False


class ResourceMonitor:
    """Comprehensive system resource monitoring."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.monitoring_interval = config.get("monitoring_interval", 5.0)
        self.alert_thresholds = config.get(
            "alert_thresholds",
            {
                "cpu_warning": 70.0,
                "cpu_critical": 90.0,
                "memory_warning": 80.0,
                "memory_critical": 95.0,
                "disk_warning": 85.0,
                "disk_critical": 95.0,
            },
        )

        # State
        self.agent_health: Dict[str, AgentHealth] = {}
        self.alerts: List[Alert] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False

        # Metrics history
        self.health_history: List[SystemHealth] = []
        self.usage_history: List[ResourceUsage] = []

        self.logger.info("ResourceMonitor initialized successfully")

    async def start_monitoring(self):
        """Start continuous monitoring."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("Resource monitoring started")

    async def stop_monitoring(self):
        """Stop continuous monitoring."""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
            self.logger.info("Resource monitoring stopped")

    async def get_system_health(self) -> SystemHealth:
        """Get current system health status."""
        try:
            # Get resource usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            network = psutil.net_io_counters()

            # Determine overall status
            overall_status = self._calculate_overall_health(
                cpu_percent, memory.percent, disk.percent
            )

            # Create system health object
            health = SystemHealth(
                overall_status=overall_status,
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                },
                timestamp=datetime.utcnow(),
            )

            # Store in history
            self.health_history.append(health)
            if len(self.health_history) > 1000:  # Keep last 1000 entries
                self.health_history = self.health_history[-1000:]

            return health

        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return SystemHealth(
                overall_status=HealthStatus.UNKNOWN,
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                timestamp=datetime.utcnow(),
            )

    async def get_resource_usage(self) -> ResourceUsage:
        """Get detailed resource usage information."""
        try:
            usage = ResourceUsage(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_percent=psutil.disk_usage("/").percent,
                network_bytes_sent=psutil.net_io_counters().bytes_sent,
                network_bytes_recv=psutil.net_io_counters().bytes_recv,
                timestamp=datetime.utcnow(),
            )

            # Store in history
            self.usage_history.append(usage)
            if len(self.usage_history) > 1000:
                self.usage_history = self.usage_history[-1000:]

            return usage

        except Exception as e:
            self.logger.error(f"Error getting resource usage: {e}")
            return ResourceUsage(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                timestamp=datetime.utcnow(),
            )

    async def get_agent_health(self) -> Dict[str, AgentHealth]:
        """Get health status of all registered agents."""
        return self.agent_health.copy()

    def register_agent(self, agent_id: str):
        """Register an agent for health monitoring."""
        self.agent_health[agent_id] = AgentHealth(
            agent_id=agent_id,
            status=HealthStatus.UNKNOWN,
            last_heartbeat=datetime.utcnow(),
            response_time=0.0,
            error_count=0,
            performance_score=1.0,
        )
        self.logger.info(f"Agent {agent_id} registered for monitoring")

    def update_agent_heartbeat(self, agent_id: str, response_time: float = 0.0):
        """Update agent heartbeat and health status."""
        if agent_id in self.agent_health:
            agent = self.agent_health[agent_id]
            agent.last_heartbeat = datetime.utcnow()
            agent.response_time = response_time

            # Update performance score based on response time
            if response_time < 0.1:
                agent.performance_score = min(1.0, agent.performance_score + 0.1)
            elif response_time > 1.0:
                agent.performance_score = max(0.0, agent.performance_score - 0.1)

            # Determine health status
            time_since_heartbeat = (
                datetime.utcnow() - agent.last_heartbeat
            ).total_seconds()
            if time_since_heartbeat > 60:  # No heartbeat for 1 minute
                agent.status = HealthStatus.CRITICAL
            elif time_since_heartbeat > 30:  # No heartbeat for 30 seconds
                agent.status = HealthStatus.WARNING
            else:
                agent.status = HealthStatus.HEALTHY

    def report_agent_error(self, agent_id: str):
        """Report an error for an agent."""
        if agent_id in self.agent_health:
            agent = self.agent_health[agent_id]
            agent.error_count += 1

            # Adjust performance score
            agent.performance_score = max(0.0, agent.performance_score - 0.2)

            # Update health status
            if agent.error_count > 10:
                agent.status = HealthStatus.CRITICAL
            elif agent.error_count > 5:
                agent.status = HealthStatus.WARNING

    def set_alert_threshold(self, metric: str, threshold: float):
        """Set alert threshold for a specific metric."""
        self.alert_thresholds[metric] = threshold
        self.logger.info(f"Alert threshold set for {metric}: {threshold}")

    async def get_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [alert for alert in self.alerts if not alert.resolved]

    def _calculate_overall_health(
        self, cpu_percent: float, memory_percent: float, disk_percent: float
    ) -> HealthStatus:
        """Calculate overall system health status."""
        # Check critical thresholds
        if (
            cpu_percent >= self.alert_thresholds.get("cpu_critical", 90.0)
            or memory_percent >= self.alert_thresholds.get("memory_critical", 95.0)
            or disk_percent >= self.alert_thresholds.get("disk_critical", 95.0)
        ):
            return HealthStatus.CRITICAL

        # Check warning thresholds
        if (
            cpu_percent >= self.alert_thresholds.get("cpu_warning", 70.0)
            or memory_percent >= self.alert_thresholds.get("memory_warning", 80.0)
            or disk_percent >= self.alert_thresholds.get("disk_warning", 85.0)
        ):
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY

    def _create_alert(self, severity: str, message: str):
        """Create a new alert."""
        alert = Alert(
            alert_id=f"alert_{len(self.alerts) + 1}",
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
        )
        self.alerts.append(alert)
        self.logger.warning(f"Alert created: {message}")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.is_monitoring:
                # Get current health and usage
                health = await self.get_system_health()
                usage = await self.get_resource_usage()

                # Check for alerts
                await self._check_alerts(health, usage)

                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)

        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            self.is_monitoring = False

    async def _check_alerts(self, health: SystemHealth, usage: ResourceUsage):
        """Check for conditions that require alerts."""
        try:
            # CPU alerts
            if usage.cpu_percent >= self.alert_thresholds.get("cpu_critical", 90.0):
                self._create_alert(
                    "critical", f"CPU usage critical: {usage.cpu_percent:.1f}%"
                )
            elif usage.cpu_percent >= self.alert_thresholds.get("cpu_warning", 70.0):
                self._create_alert(
                    "warning", f"CPU usage high: {usage.cpu_percent:.1f}%"
                )

            # Memory alerts
            if usage.memory_percent >= self.alert_thresholds.get(
                "memory_critical", 95.0
            ):
                self._create_alert(
                    "critical", f"Memory usage critical: {usage.memory_percent:.1f}%"
                )
            elif usage.memory_percent >= self.alert_thresholds.get(
                "memory_warning", 80.0
            ):
                self._create_alert(
                    "warning", f"Memory usage high: {usage.memory_percent:.1f}%"
                )

            # Disk alerts
            if usage.disk_percent >= self.alert_thresholds.get("disk_critical", 95.0):
                self._create_alert(
                    "critical", f"Disk usage critical: {usage.disk_percent:.1f}%"
                )
            elif usage.disk_percent >= self.alert_thresholds.get("disk_warning", 85.0):
                self._create_alert(
                    "warning", f"Disk usage high: {usage.disk_percent:.1f}%"
                )

            # Agent health alerts
            for agent_id, agent in self.agent_health.items():
                if agent.status == HealthStatus.CRITICAL:
                    self._create_alert("critical", f"Agent {agent_id} health critical")
                elif agent.status == HealthStatus.WARNING:
                    self._create_alert("warning", f"Agent {agent_id} health warning")

        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")

    def get_health_history(self, limit: int = 100) -> List[SystemHealth]:
        """Get recent health history."""
        return self.health_history[-limit:] if self.health_history else []

    def get_usage_history(self, limit: int = 100) -> List[ResourceUsage]:
        """Get recent usage history."""
        return self.usage_history[-limit:] if self.usage_history else []

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()
        self.logger.info("All alerts cleared")

    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                self.logger.info(f"Alert {alert_id} marked as resolved")
                break


if __name__ == "__main__":
    monitor = ResourceMonitor({"monitoring_interval": 5.0})
    print("ResourceMonitor initialized successfully!")

Resource Monitor - System Health and Resource Monitoring

This module implements the ResourceMonitor class that provides comprehensive
monitoring of system resources, agent health, and performance metrics.

import asyncio
import logging
from datetime import datetime

import psutil

class HealthStatus(Enum):

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass

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

            self.logger.info("Resource monitoring started")

    async def stop_monitoring(self):

            self.logger.info("Resource monitoring stopped")

    async def get_system_health(self) -> SystemHealth:

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

        self.logger.info(f"Agent {agent_id} registered for monitoring")

    def update_agent_heartbeat(self, agent_id: str, response_time: float = 0.0):

        self.logger.info(f"Alert threshold set for {metric}: {threshold}")

    async def get_alerts(self) -> List[Alert]:

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

            alert_id=f"alert_{len(self.alerts) + 1}",
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
        )
        self.alerts.append(alert)
        self.logger.warning(f"Alert created: {message}")

    async def _monitoring_loop(self):

            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            self.is_monitoring = False

    async def _check_alerts(self, health: SystemHealth, usage: ResourceUsage):

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

        self.logger.info("All alerts cleared")

    def resolve_alert(self, alert_id: str):

                self.logger.info(f"Alert {alert_id} marked as resolved")
                break

if __name__ == "__main__":
    monitor = ResourceMonitor({"monitoring_interval": 5.0})
    print("ResourceMonitor initialized successfully!")

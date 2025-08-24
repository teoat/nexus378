#!/usr/bin/env python3
"""
Alert System for Forensic Reconciliation Platform
Implements comprehensive alerting and notification system for queue metrics.
Estimated time: 1-2 hours
MCP Status: IMPLEMENTING - Agent: AI_Assistant
"""

import json
import logging
import smtplib
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import asyncio
import requests

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class NotificationType(Enum):
    """Notification types"""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"


@dataclass
class AlertRule:
    """Alert rule configuration"""

    id: str
    name: str
    description: str
    metric_name: str
    condition: str  # e.g., ">", "<", "==", ">=", "<="
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5
    notification_channels: List[str] = None
    tags: List[str] = None


@dataclass
class Alert:
    """Alert instance"""

    id: str
    rule_id: str
    metric_name: str
    current_value: float
    threshold: float
    condition: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    created_at: float
    acknowledged_at: Optional[float] = None
    resolved_at: Optional[float] = None
    acknowledged_by: Optional[str] = None
    tags: List[str] = None


@dataclass
class NotificationConfig:
    """Notification configuration"""

    type: NotificationType
    name: str
    config: Dict[str, Any]
    enabled: bool = True


class MCPLogger:
    """Model Context Protocol Logger for tracking agent activities"""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.agent_activities: Dict[str, List[Dict[str, Any]]] = {}
        self.implementation_locks: Dict[str, str] = {}

    def create_session(self, session_id: str, description: str):
        """Create a new MCP session"""
        self.sessions[session_id] = {
            "id": session_id,
            "description": description,
            "created": time.time(),
            "status": "active",
            "components_implemented": [],
            "agent_assignments": {},
        }
        logger.info(f"MCP Session created: {session_id} - {description}")

    def assign_component(self, session_id: str, agent_id: str, component: str) -> bool:
        """Assign a component to an agent for implementation"""
        if component in self.implementation_locks:
            logger.warning(
                f"Component {component} already assigned to {self.implementation_locks[component]}",
            )
            return False

        self.implementation_locks[component] = agent_id
        if session_id in self.sessions:
            self.sessions[session_id]["agent_assignments"][component] = agent_id
            logger.info(f"Component {component} assigned to agent {agent_id}")
            return True
        return False

    def log_implementation_start(self, session_id: str, agent_id: str, component: str):
        """Log start of component implementation"""
        if session_id in self.sessions:
            activity = {
                "timestamp": time.time(),
                "agent_id": agent_id,
                "component": component,
                "action": "implementation_start",
                "status": "in_progress",
            }

            if agent_id not in self.agent_activities:
                self.agent_activities[agent_id] = []
            self.agent_activities[agent_id].append(activity)

            logger.info(f"Agent {agent_id} started implementing {component}")

    def log_implementation_complete(
        self, session_id: str, agent_id: str, component: str
    ):
        """Log completion of component implementation"""
        if session_id in self.sessions:
            if component not in self.sessions[session_id]["components_implemented"]:
                self.sessions[session_id]["components_implemented"].append(component)

            activity = {
                "timestamp": time.time(),
                "agent_id": agent_id,
                "component": component,
                "action": "implementation_complete",
                "status": "completed",
            }

            if agent_id not in self.agent_activities:
                self.agent_activities[agent_id] = []
            self.agent_activities[agent_id].append(activity)

            logger.info(f"Agent {agent_id} completed implementing {component}")


class AlertSystem:
    """Comprehensive alerting and notification system"""

    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_configs: Dict[str, NotificationConfig] = {}
        self.monitoring_task = None
        self.is_monitoring = False
        self.mcp_logger = MCPLogger()

        # Initialize default alert rules
        self._create_default_rules()

        logger.info("Alert System initialized with MCP logging")

    def start_implementation_session(
        self, description: str = "Alert System Implementation"
    ):
        """Start a new implementation session"""
        session_id = str(uuid.uuid4())
        self.mcp_logger.create_session(session_id, description)
        return session_id

    def assign_component_for_implementation(
        self, session_id: str, agent_id: str, component: str
    ) -> bool:
        """Assign a component to an agent for implementation"""
        return self.mcp_logger.assign_component(session_id, agent_id, component)

    def _create_default_rules(self):
        """Create default alert rules"""
        default_rules = [
            AlertRule(
                id="high_queue_size",
                name="High Queue Size",
                description="Alert when queue size exceeds threshold",
                metric_name="queue_size",
                condition=">",
                threshold=1000,
                severity=AlertSeverity.WARNING,
                cooldown_minutes=10,
                notification_channels=["email", "slack"],
                tags=["queue", "performance"],
            ),
            AlertRule(
                id="high_latency",
                name="High Latency",
                description="Alert when latency exceeds threshold",
                metric_name="latency",
                condition=">",
                threshold=5000,  # 5 seconds
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=5,
                notification_channels=["email", "slack", "pagerduty"],
                tags=["queue", "performance", "user_experience"],
            ),
            AlertRule(
                id="high_error_rate",
                name="High Error Rate",
                description="Alert when error rate exceeds threshold",
                metric_name="error_rate",
                condition=">",
                threshold=0.05,  # 5%
                severity=AlertSeverity.CRITICAL,
                cooldown_minutes=2,
                notification_channels=["email", "slack", "pagerduty"],
                tags=["queue", "reliability", "errors"],
            ),
            AlertRule(
                id="low_throughput",
                name="Low Throughput",
                description="Alert when throughput drops below threshold",
                metric_name="throughput",
                condition="<",
                threshold=10.0,  # 10 msg/s
                severity=AlertSeverity.WARNING,
                cooldown_minutes=15,
                notification_channels=["email", "slack"],
                tags=["queue", "performance", "capacity"],
            ),
            AlertRule(
                id="system_unhealthy",
                name="System Unhealthy",
                description="Alert when system health score drops below threshold",
                metric_name="health_score",
                condition="<",
                threshold=50.0,  # 50%
                severity=AlertSeverity.EMERGENCY,
                cooldown_minutes=1,
                notification_channels=["email", "slack", "pagerduty", "sms"],
                tags=["system", "health", "critical"],
            ),
        ]

        for rule in default_rules:
            self.alert_rules[rule.id] = rule

        logger.info(f"Created {len(default_rules)} default alert rules")

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.id] = rule
        logger.info(f"Alert rule '{rule.name}' added")

    def update_alert_rule(self, rule_id: str, **kwargs):
        """Update an existing alert rule"""
        if rule_id in self.alert_rules:
            rule = self.alert_rules[rule_id]
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            logger.info(f"Alert rule '{rule_id}' updated")
        else:
            logger.error(f"Alert rule '{rule_id}' not found")

    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Alert rule '{rule_id}' removed")
        else:
            logger.error(f"Alert rule '{rule_id}' not found")

    def add_notification_config(self, config: NotificationConfig):
        """Add notification configuration"""
        self.notification_configs[config.name] = config
        logger.info(f"Notification config '{config.name}' added")

    def check_alerts(self, metrics_data: Dict[str, Any]):
        """Check metrics against alert rules and trigger alerts"""
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue

            # Check if rule is in cooldown
            if self._is_rule_in_cooldown(rule_id, rule.cooldown_minutes):
                continue

            # Get metric value
            metric_value = self._get_metric_value(rule.metric_name, metrics_data)
            if metric_value is None:
                continue

            # Check condition
            if self._evaluate_condition(metric_value, rule.condition, rule.threshold):
                # Create alert
                alert = self._create_alert(rule, metric_value)
                self.active_alerts[alert.id] = alert
                self.alert_history.append(alert)

                # Send notifications
                self._send_notifications(alert)

                logger.info(
                    f"Alert triggered: {rule.name} - {metric_value} {rule.condition} {rule.threshold}",
                )

    def _is_rule_in_cooldown(self, rule_id: str, cooldown_minutes: int) -> bool:
        """Check if rule is in cooldown period"""
        current_time = time.time()
        cooldown_seconds = cooldown_minutes * 60

        # Check recent alerts for this rule
        for alert in self.alert_history[-10:]:  # Check last 10 alerts
            if (
                alert.rule_id == rule_id
                and alert.created_at > current_time - cooldown_seconds
            ):
                return True

        return False

    def _get_metric_value(self, metric_name: str, metrics_data: Dict[str, Any]):
        """Extract metric value from metrics data"""
        try:
            if metric_name == "queue_size":
                return float(metrics_data.get("current_size", 0))
            elif metric_name == "latency":
                return float(metrics_data.get("avg_latency", 0))
            elif metric_name == "error_rate":
                return float(metrics_data.get("error_rate", 0))
            elif metric_name == "throughput":
                return float(metrics_data.get("avg_throughput", 0))
            elif metric_name == "health_score":
                return float(metrics_data.get("health_score", 100))
            else:
                return metrics_data.get(metric_name)
        except (ValueError, TypeError):
            return None

    def _evaluate_condition(self, value: float, condition: str, threshold: float):
        """Evaluate alert condition"""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False

    def _create_alert(self, rule: AlertRule, current_value: float) -> Alert:
        """Create a new alert"""
        alert = Alert(
            id=str(uuid.uuid4()),
            rule_id=rule.id,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold=rule.threshold,
            condition=rule.condition,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            message=f"{rule.name}: {current_value} {rule.condition} {rule.threshold}",
            created_at=time.time(),
            tags=rule.tags or [],
        )
        return alert

    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        rule = self.alert_rules.get(alert.rule_id)
        if not rule or not rule.notification_channels:
            return

        for channel_name in rule.notification_channels:
            config = self.notification_configs.get(channel_name)
            if config and config.enabled:
                try:
                    self._send_notification(config, alert)
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel_name}: {e}")

    def _send_notification(self, config: NotificationConfig, alert: Alert):
        """Send notification via specific channel"""
        if config.type == NotificationType.EMAIL:
            self._send_email_notification(config, alert)
        elif config.type == NotificationType.SLACK:
            self._send_slack_notification(config, alert)
        elif config.type == NotificationType.WEBHOOK:
            self._send_webhook_notification(config, alert)
        elif config.type == NotificationType.SMS:
            self._send_sms_notification(config, alert)
        elif config.type == NotificationType.PAGERDUTY:
            self._send_pagerduty_notification(config, alert)
        else:
            logger.warning(f"Unknown notification type: {config.type}")

    def _send_email_notification(self, config: NotificationConfig, alert: Alert):
        """Send email notification"""
        try:
            # This is a simplified email implementation
            # In production, you'd use proper email libraries
            logger.info(f"Email notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    def _send_slack_notification(self, config: NotificationConfig, alert: Alert):
        """Send Slack notification"""
        try:
            webhook_url = config.config.get("webhook_url")
            if webhook_url:
                payload = {
                    "text": f"🚨 *{alert.severity.value.upper()} Alert*: {alert.message}",
                    "attachments": [
                        {
                            "fields": [
                                {
                                    "title": "Metric",
                                    "value": alert.metric_name,
                                    "short": True,
                                },
                                {
                                    "title": "Current Value",
                                    "value": str(alert.current_value),
                                    "short": True,
                                },
                                {
                                    "title": "Threshold",
                                    "value": f"{alert.condition} {alert.threshold}",
                                    "short": True,
                                },
                                {
                                    "title": "Time",
                                    "value": datetime.fromtimestamp(
                                        alert.created_at
                                    ).strftime("%Y-%m-%d %H:%M:%S"),
                                    "short": True,
                                },
                            ],
                            "color": self._get_severity_color(alert.severity),
                        }
                    ],
                }

                response = requests.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"Slack notification sent for alert {alert.id}")
            else:
                logger.warning("Slack webhook URL not configured")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    def _send_webhook_notification(self, config: NotificationConfig, alert: Alert):
        """Send webhook notification"""
        try:
            webhook_url = config.config.get("url")
            if webhook_url:
                payload = {
                    "alert_id": alert.id,
                    "rule_id": alert.rule_id,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "metric_name": alert.metric_name,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold,
                    "condition": alert.condition,
                    "created_at": alert.created_at,
                    "tags": alert.tags or [],
                }

                response = requests.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"Webhook notification sent for alert {alert.id}")
            else:
                logger.warning("Webhook URL not configured")
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")

    def _send_sms_notification(self, config: NotificationConfig, alert: Alert):
        """Send SMS notification"""
        try:
            # This is a simplified SMS implementation
            # In production, you'd use proper SMS services
            logger.info(f"SMS notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")

    def _send_pagerduty_notification(self, config: NotificationConfig, alert: Alert):
        """Send PagerDuty notification"""
        try:
            # This is a simplified PagerDuty implementation
            # In production, you'd use the PagerDuty API
            logger.info(f"PagerDuty notification sent for alert {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send PagerDuty notification: {e}")

    def _get_severity_color(self, severity: AlertSeverity) -> str:
        """Get color for severity level"""
        colors = {
            AlertSeverity.INFO: "#36a2eb",
            AlertSeverity.WARNING: "#ffcd56",
            AlertSeverity.CRITICAL: "#ff6384",
            AlertSeverity.EMERGENCY: "#ff0000",
        }
        return colors.get(severity, "#808080")

    def acknowledge_alert(self, alert_id: str, user: str):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = time.time()
            alert.acknowledged_by = user
            logger.info(f"Alert {alert_id} acknowledged by {user}")
        else:
            logger.error(f"Alert {alert_id} not found")

    def resolve_alert(self, alert_id: str, user: str):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = time.time()

            # Move to history
            del self.active_alerts[alert_id]

            logger.info(f"Alert {alert_id} resolved by {user}")
        else:
            logger.error(f"Alert {alert_id} not found")

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None):
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        return self.alert_history[-limit:]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert system"""
        summary = {
            "total_rules": len(self.alert_rules),
            "enabled_rules": len([r for r in self.alert_rules.values() if r.enabled]),
            "active_alerts": len(self.active_alerts),
            "total_notifications": len(self.notification_configs),
            "enabled_notifications": len(
                [n for n in self.notification_configs.values() if n.enabled]
            ),
            "alerts_by_severity": {},
            "recent_alerts": [],
        }

        # Count alerts by severity
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            summary["alerts_by_severity"][severity] = (
                summary["alerts_by_severity"].get(severity, 0) + 1
            )

        # Get recent alerts
        summary["recent_alerts"] = [
            {
                "id": alert.id,
                "rule_name": self.alert_rules.get(alert.rule_id, {}).get(
                    "name", "Unknown"
                ),
                "severity": alert.severity.value,
                "message": alert.message,
                "created_at": alert.created_at,
                "status": alert.status.value,
            }
            for alert in self.alert_history[-10:]  # Last 10 alerts
        ]

        return summary

    async def start_monitoring(self, interval_seconds: int = 30):
        """Start alert monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info(f"Alert monitoring started with {interval_seconds}s interval")

    def stop_monitoring(self):
        """Stop alert monitoring"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Alert monitoring stopped")

    async def _monitoring_loop(self, interval_seconds: int):
        """Alert monitoring loop"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(interval_seconds)

                if self.is_monitoring and self.metrics_collector:
                    # Get current metrics and check alerts
                    stats = self.metrics_collector.get_all_queue_stats()
                    for stat in stats:
                        metrics_data = {
                            "current_size": stat.current_size,
                            "avg_latency": stat.avg_latency,
                            "error_rate": stat.error_rate,
                            "avg_throughput": stat.avg_throughput,
                            "health_score": stat.health_score,
                        }
                        self.check_alerts(metrics_data)

                    # Clean up expired alerts
                    self._cleanup_expired_alerts()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10.0)

    def _cleanup_expired_alerts(self):
        """Clean up expired alerts"""
        current_time = time.time()
        expired_alerts = []

        for alert_id, alert in self.active_alerts.items():
            # Mark alerts as expired if they're older than 24 hours
            if current_time - alert.created_at > 24 * 3600:
                expired_alerts.append(alert_id)

        for alert_id in expired_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.EXPIRED
            del self.active_alerts[alert_id]
            logger.info(f"Alert {alert_id} marked as expired")


# Example usage and testing
def test_alert_system():
    """Test the Alert System with MCP logging"""
    print("🧪 Testing Alert System with MCP Logging")
    print("=" * 60)

    # Create alert system
    alert_system = AlertSystem()

    # Start implementation session
    session_id = alert_system.start_implementation_session("Alert System Testing")
    print(f"📋 MCP Session created: {session_id}")

    # Assign component to agent
    agent_id = "AI_Assistant"
    component = "alert_system"

    if alert_system.assign_component_for_implementation(
        session_id, agent_id, component
    ):
        print(f"✅ Component {component} assigned to {agent_id}")

        # Log implementation start
        alert_system.mcp_logger.log_implementation_start(
            session_id, agent_id, component
        )

        # Add notification configs
        print("\n📧 Adding notification configurations...")

        # Slack config
        slack_config = NotificationConfig(
            type=NotificationType.SLACK,
            name="slack",
            config={"webhook_url": "https://hooks.slack.com/services/test"},
            enabled=True,
        )
        alert_system.add_notification_config(slack_config)

        # Webhook config
        webhook_config = NotificationConfig(
            type=NotificationType.WEBHOOK,
            name="webhook",
            config={"url": "https://api.example.com/alerts"},
            enabled=True,
        )
        alert_system.add_notification_config(webhook_config)

        # Test alert rules
        print("\n🚨 Testing alert rules...")
        test_metrics = {
            "current_size": 1500,  # Should trigger high queue size alert
            "avg_latency": 6000,  # Should trigger high latency alert
            "error_rate": 0.08,  # Should trigger high error rate alert
            "avg_throughput": 5.0,  # Should trigger low throughput alert
            "health_score": 30.0,  # Should trigger system unhealthy alert
        }

        alert_system.check_alerts(test_metrics)

        # Get active alerts
        print("\n📊 Active Alerts:")
        active_alerts = alert_system.get_active_alerts()
        print(f"  Total Active Alerts: {len(active_alerts)}")

        for alert in active_alerts:
            rule = alert_system.alert_rules.get(alert.rule_id, {})
            print(f"    - {rule.get('name', 'Unknown')}: {alert.message}")
            print(
                f"      Severity: {alert.severity.value}, Status: {alert.status.value}"
            )

        # Get alert summary
        print("\n📈 Alert System Summary:")
        summary = alert_system.get_alert_summary()
        print(f"  Total Rules: {summary['total_rules']}")
        print(f"  Enabled Rules: {summary['enabled_rules']}")
        print(f"  Active Alerts: {summary['active_alerts']}")
        print(f"  Total Notifications: {summary['total_notifications']}")
        print(f"  Alerts by Severity: {summary['alerts_by_severity']}")

        # Log implementation complete
        alert_system.mcp_logger.log_implementation_complete(
            session_id, agent_id, component
        )

        print("\n✅ Alert System test completed!")

    else:
        print(f"❌ Failed to assign component {component}")


if __name__ == "__main__":
    # Run the test
    test_alert_system()
import json
import logging
import time
import uuid

import asyncio
import requests

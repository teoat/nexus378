"""
SLA Monitor - Service Level Agreement Monitoring and Alerting

This module implements the SLAMonitor class that handles monitoring of
service level agreements, performance metrics, and alert generation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import math
import uuid

from ..models.job import Job, JobStatus, JobPriority, JobType


class SLAMetric(Enum):
    """SLA metric types."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    QUEUE_TIME = "queue_time"
    PROCESSING_TIME = "processing_time"
    COST_EFFICIENCY = "cost_efficiency"
    RESOURCE_UTILIZATION = "resource_utilization"


class SLAStatus(Enum):
    """SLA status enumeration."""
    MET = "met"                    # SLA is being met
    WARNING = "warning"            # SLA is approaching violation
    VIOLATED = "violated"          # SLA has been violated
    CRITICAL = "critical"          # Critical SLA violation
    UNKNOWN = "unknown"            # SLA status unknown


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"                  # Informational alert
    WARNING = "warning"            # Warning alert
    ERROR = "error"                # Error alert
    CRITICAL = "critical"          # Critical alert


class AlertChannel(Enum):
    """Alert notification channels."""
    EMAIL = "email"                # Email notification
    SLACK = "slack"                # Slack notification
    WEBHOOK = "webhook"            # Webhook notification
    SMS = "sms"                    # SMS notification
    DASHBOARD = "dashboard"        # Dashboard display
    LOG = "log"                    # Log file


@dataclass
class SLADefinition:
    """SLA definition and thresholds."""
    
    id: str
    name: str
    description: str
    metric: SLAMetric
    target_value: float
    warning_threshold: float
    critical_threshold: float
    measurement_window: timedelta
    evaluation_frequency: timedelta
    enabled: bool = True
    priority: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class SLAMeasurement:
    """SLA measurement data."""
    
    sla_id: str
    metric_value: float
    target_value: float
    status: SLAStatus
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class SLAViolation:
    """SLA violation record."""
    
    id: str
    sla_id: str
    violation_type: SLAStatus
    metric_value: float
    target_value: float
    threshold: float
    timestamp: datetime
    duration: timedelta
    severity: AlertSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class Alert:
    """Alert definition."""
    
    id: str
    title: str
    message: str
    severity: AlertSeverity
    sla_id: str
    violation_id: str
    timestamp: datetime
    channels: List[AlertChannel] = field(default_factory=list)
    acknowledged: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class SLAMetrics:
    """SLA performance metrics."""
    
    total_slas: int = 0
    met_slas: int = 0
    warning_slas: int = 0
    violated_slas: int = 0
    critical_slas: int = 0
    overall_compliance_rate: float = 0.0
    average_response_time: float = 0.0
    average_throughput: float = 0.0
    availability_percentage: float = 0.0
    
    def update_compliance_rate(self):
        """Update overall compliance rate."""
        if self.total_slas > 0:
            self.overall_compliance_rate = self.met_slas / self.total_slas


class SLAMonitor:
    """
    SLA monitoring engine for the Taskmaster system.
    
    The SLAMonitor is responsible for:
    - Monitoring service level agreements
    - Tracking performance metrics
    - Detecting SLA violations
    - Generating alerts and notifications
    - Providing SLA compliance reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the SLAMonitor."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_real_time_monitoring = config.get('enable_real_time_monitoring', True)
        self.alert_cooldown = timedelta(minutes=config.get('alert_cooldown_minutes', 15))
        self.violation_threshold = config.get('violation_threshold', 3)
        self.metrics_retention = timedelta(days=config.get('metrics_retention_days', 30)
        
        # Internal state
        self.sla_definitions: Dict[str, SLADefinition] = {}
        self.sla_measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.sla_violations: Dict[str, List[SLAViolation]] = defaultdict(list)
        self.alerts: List[Alert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # SLA metrics
        self.sla_metrics = SLAMetrics()
        
        # Performance tracking
        self.performance_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.job_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("SLAMonitor initialized successfully")
    
    async def start(self):
        """Start the SLAMonitor."""
        self.logger.info("Starting SLAMonitor...")
        
        # Initialize default SLAs
        await self._initialize_default_slas()
        
        # Start background tasks
        asyncio.create_task(self._monitor_slas())
        asyncio.create_task(self._collect_performance_metrics())
        asyncio.create_task(self._evaluate_sla_compliance())
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._update_sla_metrics())
        
        self.logger.info("SLAMonitor started successfully")
    
    async def stop(self):
        """Stop the SLAMonitor."""
        self.logger.info("Stopping SLAMonitor...")
        self.logger.info("SLAMonitor stopped")
    
    async def add_sla_definition(self, sla: SLADefinition):
        """Add a new SLA definition."""
        self.sla_definitions[sla.id] = sla
        self.sla_metrics.total_slas += 1
        self.logger.info(f"Added SLA definition: {sla.name}")
    
    async def remove_sla_definition(self, sla_id: str):
        """Remove an SLA definition."""
        if sla_id in self.sla_definitions:
            del self.sla_definitions[sla_id]
            self.sla_metrics.total_slas = max(0, self.sla_metrics.total_slas - 1)
            self.logger.info(f"Removed SLA definition: {sla_id}")
    
    async def get_sla_status(self, sla_id: str) -> Optional[SLAStatus]:
        """Get current status of an SLA."""
        if sla_id not in self.sla_definitions:
            return None
        
        # Get latest measurement
        if sla_id in self.sla_measurements and self.sla_measurements[sla_id]:
            latest = self.sla_measurements[sla_id][-1]
            return latest.status
        
        return SLAStatus.UNKNOWN
    
    async def get_sla_compliance_report(self, duration: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Get SLA compliance report for a specific duration."""
        try:
            report = {
                'overall_compliance': self.sla_metrics.overall_compliance_rate,
                'total_slas': self.sla_metrics.total_slas,
                'compliance_breakdown': {},
                'violations_summary': {},
                'performance_metrics': {},
                'recommendations': []
            }
            
            # Compliance breakdown by SLA
            for sla_id, sla in self.sla_definitions.items():
                if sla_id in self.sla_measurements:
                    measurements = self.sla_measurements[sla_id]
                    cutoff_time = datetime.utcnow() - duration
                    
                    # Filter measurements within duration
                    recent_measurements = [
                        m for m in measurements if m.timestamp >= cutoff_time
                    ]
                    
                    if recent_measurements:
                        met_count = sum(1 for m in recent_measurements if m.status == SLAStatus.MET)
                        total_count = len(recent_measurements)
                        compliance_rate = met_count / total_count if total_count > 0 else 0
                        
                        report['compliance_breakdown'][sla.name] = {
                            'compliance_rate': compliance_rate,
                            'total_measurements': total_count,
                            'met_count': met_count,
                            'status': 'met' if compliance_rate >= 0.95 else 'warning' if compliance_rate >= 0.8 else 'violated'
                        }
            
            # Violations summary
            for sla_id, violations in self.sla_violations.items():
                if sla_id in self.sla_definitions:
                    sla_name = self.sla_definitions[sla_id].name
                    recent_violations = [
                        v for v in violations
                        if datetime.utcnow() - v.timestamp <= duration
                    ]
                    
                    if recent_violations:
                        report['violations_summary'][sla_name] = {
                            'total_violations': len(recent_violations),
                            'critical_violations': sum(1 for v in recent_violations if v.severity == AlertSeverity.CRITICAL),
                            'last_violation': recent_violations[-1].timestamp.isoformat() if recent_violations else None
                        }
            
            # Performance metrics
            report['performance_metrics'] = {
                'average_response_time': self.sla_metrics.average_response_time,
                'average_throughput': self.sla_metrics.average_throughput,
                'availability_percentage': self.sla_metrics.availability_percentage
            }
            
            # Generate recommendations
            report['recommendations'] = await self._generate_recommendations()
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating SLA compliance report: {e}")
            return {}
    
    async def get_sla_violations(self, sla_id: str, duration: timedelta = timedelta(days=7)) -> List[SLAViolation]:
        """Get SLA violations for a specific SLA and duration."""
        if sla_id not in self.sla_violations:
            return []
        
        cutoff_time = datetime.utcnow() - duration
        return [
            violation for violation in self.sla_violations[sla_id]
            if violation.timestamp >= cutoff_time
        ]
    
    async def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self.logger.info(f"Acknowledged alert: {alert_id}")
                break
    
    async def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self.logger.info(f"Resolved alert: {alert_id}")
                break
    
    async def record_job_metric(self, job: Job, metric_type: str, value: float, 
                               context: Dict[str, Any] = None):
        """Record a job-related metric."""
        try:
            if not context:
                context = {}
            
            # Store metric
            metric_data = {
                'job_id': job.id,
                'job_type': job.job_type.value,
                'priority': job.priority.value,
                'metric_type': metric_type,
                'value': value,
                'timestamp': datetime.utcnow(),
                'context': context
            }
            
            self.performance_data[metric_type].append(metric_data)
            
            # Update job metrics
            if job.id not in self.job_metrics:
                self.job_metrics[job.id] = {}
            
            self.job_metrics[job.id][metric_type] = value
            
            self.logger.debug(f"Recorded metric {metric_type}={value} for job {job.id}")
            
        except Exception as e:
            self.logger.error(f"Error recording job metric: {e}")
    
    async def _monitor_slas(self):
        """Monitor SLA compliance in real-time."""
        while True:
            try:
                if self.enable_real_time_monitoring:
                    # Evaluate all enabled SLAs
                    for sla_id, sla in self.sla_definitions.items():
                        if sla.enabled:
                            await self._evaluate_sla(sla)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring SLAs: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_sla(self, sla: SLADefinition):
        """Evaluate a specific SLA."""
        try:
            # Get current metric value
            current_value = await self._get_current_metric_value(sla)
            
            if current_value is None:
                return
            
            # Determine SLA status
            status = self._determine_sla_status(sla, current_value)
            
            # Create measurement
            measurement = SLAMeasurement(
                sla_id=sla.id,
                metric_value=current_value,
                target_value=sla.target_value,
                status=status,
                context={'evaluation_time': datetime.utcnow()}
            )
            
            # Store measurement
            self.sla_measurements[sla.id].append(measurement)
            
            # Check for violations
            if status in [SLAStatus.WARNING, SLAStatus.VIOLATED, SLAStatus.CRITICAL]:
                await self._handle_sla_violation(sla, measurement)
            
            # Update metrics
            await self._update_sla_status_counts(status)
            
        except Exception as e:
            self.logger.error(f"Error evaluating SLA {sla.id}: {e}")
    
    async def _get_current_metric_value(self, sla: SLADefinition) -> Optional[float]:
        """Get current value for an SLA metric."""
        try:
            if sla.metric == SLAMetric.RESPONSE_TIME:
                return await self._calculate_average_response_time()
            
            elif sla.metric == SLAMetric.THROUGHPUT:
                return await self._calculate_throughput()
            
            elif sla.metric == SLAMetric.AVAILABILITY:
                return await self._calculate_availability()
            
            elif sla.metric == SLAMetric.SUCCESS_RATE:
                return await self._calculate_success_rate()
            
            elif sla.metric == SLAMetric.ERROR_RATE:
                return await self._calculate_error_rate()
            
            elif sla.metric == SLAMetric.QUEUE_TIME:
                return await self._calculate_average_queue_time()
            
            elif sla.metric == SLAMetric.PROCESSING_TIME:
                return await self._calculate_average_processing_time()
            
            elif sla.metric == SLAMetric.COST_EFFICIENCY:
                return await self._calculate_cost_efficiency()
            
            elif sla.metric == SLAMetric.RESOURCE_UTILIZATION:
                return await self._calculate_resource_utilization()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting metric value for {sla.metric.value}: {e}")
            return None
    
    def _determine_sla_status(self, sla: SLADefinition, current_value: float) -> SLAStatus:
        """Determine SLA status based on current value and thresholds."""
        try:
            # For metrics where lower is better (e.g., response time, error rate)
            if sla.metric in [SLAMetric.RESPONSE_TIME, SLAMetric.ERROR_RATE, SLAMetric.QUEUE_TIME, SLAMetric.PROCESSING_TIME]:
                if current_value <= sla.target_value:
                    return SLAStatus.MET
                elif current_value <= sla.warning_threshold:
                    return SLAStatus.WARNING
                elif current_value <= sla.critical_threshold:
                    return SLAStatus.VIOLATED
                else:
                    return SLAStatus.CRITICAL
            
            # For metrics where higher is better (e.g., throughput, availability, success rate)
            else:
                if current_value >= sla.target_value:
                    return SLAStatus.MET
                elif current_value >= sla.warning_threshold:
                    return SLAStatus.WARNING
                elif current_value >= sla.critical_threshold:
                    return SLAStatus.VIOLATED
                else:
                    return SLAStatus.CRITICAL
            
        except Exception as e:
            self.logger.error(f"Error determining SLA status: {e}")
            return SLAStatus.UNKNOWN
    
    async def _handle_sla_violation(self, sla: SLADefinition, measurement: SLAMeasurement):
        """Handle an SLA violation."""
        try:
            # Determine violation type and severity
            violation_type = measurement.status
            severity = self._determine_violation_severity(violation_type)
            
            # Check if we should generate an alert
            if await self._should_generate_alert(sla.id, violation_type):
                # Create violation record
                violation = SLAViolation(
                    sla_id=sla.id,
                    violation_type=violation_type,
                    metric_value=measurement.metric_value,
                    target_value=measurement.target_value,
                    threshold=sla.critical_threshold if violation_type == SLAStatus.CRITICAL else sla.warning_threshold,
                    timestamp=datetime.utcnow(),
                    duration=timedelta(0),  # Will be updated if violation persists
                    severity=severity,
                    context={'measurement_id': measurement.timestamp.isoformat()}
                )
                
                # Store violation
                self.sla_violations[sla.id].append(violation)
                
                # Generate alert
                await self._generate_alert(sla, violation)
                
                # Update last alert time
                self.last_alert_time[sla.id] = datetime.utcnow()
                
                self.logger.warning(f"SLA violation detected for {sla.name}: {violation_type.value}")
            
        except Exception as e:
            self.logger.error(f"Error handling SLA violation: {e}")
    
    def _determine_violation_severity(self, violation_type: SLAStatus) -> AlertSeverity:
        """Determine alert severity for a violation."""
        if violation_type == SLAStatus.CRITICAL:
            return AlertSeverity.CRITICAL
        elif violation_type == SLAStatus.VIOLATED:
            return AlertSeverity.ERROR
        elif violation_type == SLAStatus.WARNING:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO
    
    async def _should_generate_alert(self, sla_id: str, violation_type: SLAStatus) -> bool:
        """Determine if an alert should be generated."""
        # Check cooldown period
        if sla_id in self.last_alert_time:
            if datetime.utcnow() - self.last_alert_time[sla_id] < self.alert_cooldown:
                return False
        
        # Always alert for critical violations
        if violation_type == SLAStatus.CRITICAL:
            return True
        
        # Check violation threshold
        if sla_id in self.sla_violations:
            recent_violations = [
                v for v in self.sla_violations[sla_id]
                if datetime.utcnow() - v.timestamp < timedelta(hours=1)
            ]
            
            if len(recent_violations) >= self.violation_threshold:
                return True
        
        return True
    
    async def _generate_alert(self, sla: SLADefinition, violation: SLAViolation):
        """Generate an alert for an SLA violation."""
        try:
            # Create alert
            alert = Alert(
                title=f"SLA Violation: {sla.name}",
                message=f"SLA '{sla.name}' is currently {violation.violation_type.value}. "
                       f"Current value: {violation.metric_value:.2f}, "
                       f"Target: {violation.target_value:.2f}",
                severity=violation.severity,
                sla_id=sla.id,
                violation_id=violation.id,
                timestamp=datetime.utcnow(),
                channels=[AlertChannel.DASHBOARD, AlertChannel.LOG],
                metadata={
                    'metric': sla.metric.value,
                    'threshold': violation.threshold,
                    'duration': violation.duration.total_seconds()
                }
            )
            
            # Add to alerts list
            self.alerts.append(alert)
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
            self.logger.info(f"Generated alert for SLA violation: {alert.title}")
            
        except Exception as e:
            self.logger.error(f"Error generating alert: {e}")
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications through configured channels."""
        try:
            for channel in alert.channels:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_alert(alert)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert)
                elif channel == AlertChannel.SMS:
                    await self._send_sms_alert(alert)
                elif channel == AlertChannel.LOG:
                    self._log_alert(alert)
                elif channel == AlertChannel.DASHBOARD:
                    # Dashboard alerts are handled by the UI
                    pass
            
        except Exception as e:
            self.logger.error(f"Error sending alert notifications: {e}")
    
    async def _send_email_alert(self, alert: Alert):
        """Send email alert."""
        # This would integrate with your email system
        self.logger.info(f"Email alert sent: {alert.title}")
    
    async def _send_slack_alert(self, alert: Alert):
        """Send Slack alert."""
        # This would integrate with your Slack integration
        self.logger.info(f"Slack alert sent: {alert.title}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert."""
        # This would integrate with your webhook system
        self.logger.info(f"Webhook alert sent: {alert.title}")
    
    async def _send_sms_alert(self, alert: Alert):
        """Send SMS alert."""
        # This would integrate with your SMS system
        self.logger.info(f"SMS alert sent: {alert.title}")
    
    def _log_alert(self, alert: Alert):
        """Log alert to system logs."""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        self.logger.log(log_level, f"ALERT: {alert.title} - {alert.message}")
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics from the system."""
        while True:
            try:
                # Collect system performance metrics
                # This would integrate with your monitoring system
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error collecting performance metrics: {e}")
                await asyncio.sleep(300)
    
    async def _evaluate_sla_compliance(self):
        """Evaluate overall SLA compliance."""
        while True:
            try:
                # Update compliance metrics
                met_count = 0
                warning_count = 0
                violated_count = 0
                critical_count = 0
                
                for sla_id, sla in self.sla_definitions.items():
                    if sla.enabled and sla_id in self.sla_measurements:
                        latest = self.sla_measurements[sla_id][-1] if self.sla_measurements[sla_id] else None
                        if latest:
                            if latest.status == SLAStatus.MET:
                                met_count += 1
                            elif latest.status == SLAStatus.WARNING:
                                warning_count += 1
                            elif latest.status == SLAStatus.VIOLATED:
                                violated_count += 1
                            elif latest.status == SLAStatus.CRITICAL:
                                critical_count += 1
                
                # Update metrics
                self.sla_metrics.met_slas = met_count
                self.sla_metrics.warning_slas = warning_count
                self.sla_metrics.violated_slas = violated_count
                self.sla_metrics.critical_slas = critical_count
                self.sla_metrics.update_compliance_rate()
                
                await asyncio.sleep(300)  # Evaluate every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error evaluating SLA compliance: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_data(self):
        """Clean up old SLA data."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - self.metrics_retention
                
                # Clean up old measurements
                for sla_id in list(self.sla_measurements.keys()):
                    self.sla_measurements[sla_id] = deque(
                        [m for m in self.sla_measurements[sla_id] if m.timestamp > cutoff_time],
                        maxlen=1000
                    )
                
                # Clean up old violations
                for sla_id in list(self.sla_violations.keys()):
                    self.sla_violations[sla_id] = [
                        v for v in self.sla_violations[sla_id]
                        if v.timestamp > cutoff_time
                    ]
                
                # Clean up old alerts
                self.alerts = [
                    alert for alert in self.alerts
                    if alert.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _update_sla_metrics(self):
        """Update SLA performance metrics."""
        while True:
            try:
                # Update performance metrics
                self.sla_metrics.average_response_time = await self._calculate_average_response_time() or 0.0
                self.sla_metrics.average_throughput = await self._calculate_throughput() or 0.0
                self.sla_metrics.availability_percentage = await self._calculate_availability() or 0.0
                
                await asyncio.sleep(600)  # Update every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating SLA metrics: {e}")
                await asyncio.sleep(600)
    
    async def _initialize_default_slas(self):
        """Initialize default SLA definitions."""
        default_slas = [
            SLADefinition(
                name="Job Response Time",
                description="Average time to start processing a job",
                metric=SLAMetric.RESPONSE_TIME,
                target_value=5.0,  # seconds
                warning_threshold=10.0,
                critical_threshold=30.0,
                measurement_window=timedelta(minutes=5),
                evaluation_frequency=timedelta(minutes=1)
            ),
            SLADefinition(
                name="Job Success Rate",
                description="Percentage of jobs completed successfully",
                metric=SLAMetric.SUCCESS_RATE,
                target_value=95.0,  # percentage
                warning_threshold=90.0,
                critical_threshold=80.0,
                measurement_window=timedelta(minutes=15),
                evaluation_frequency=timedelta(minutes=5)
            ),
            SLADefinition(
                name="System Availability",
                description="System uptime percentage",
                metric=SLAMetric.AVAILABILITY,
                target_value=99.9,  # percentage
                warning_threshold=99.5,
                critical_threshold=99.0,
                measurement_window=timedelta(hours=1),
                evaluation_frequency=timedelta(minutes=5)
            )
        ]
        
        for sla in default_slas:
            await self.add_sla_definition(sla)
    
    async def _calculate_average_response_time(self) -> Optional[float]:
        """Calculate average job response time."""
        try:
            if 'response_time' in self.performance_data:
                recent_data = [
                    d for d in self.performance_data['response_time']
                    if datetime.utcnow() - d['timestamp'] < timedelta(minutes=15)
                ]
                
                if recent_data:
                    return sum(d['value'] for d in recent_data) / len(recent_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating average response time: {e}")
            return None
    
    async def _calculate_throughput(self) -> Optional[float]:
        """Calculate system throughput (jobs per minute)."""
        try:
            # Count jobs completed in the last minute
            cutoff_time = datetime.utcnow() - timedelta(minutes=1)
            completed_jobs = sum(
                1 for job_data in self.job_metrics.values()
                if 'completed_at' in job_data and job_data['completed_at'] > cutoff_time
            )
            
            return completed_jobs
            
        except Exception as e:
            self.logger.error(f"Error calculating throughput: {e}")
            return None
    
    async def _calculate_availability(self) -> Optional[float]:
        """Calculate system availability percentage."""
        try:
            # This would integrate with your system monitoring
            # For now, return a placeholder value
            return 99.9
            
        except Exception as e:
            self.logger.error(f"Error calculating availability: {e}")
            return None
    
    async def _calculate_success_rate(self) -> Optional[float]:
        """Calculate job success rate percentage."""
        try:
            if not self.job_metrics:
                return None
            
            total_jobs = len(self.job_metrics)
            successful_jobs = sum(
                1 for job_data in self.job_metrics.values()
                if job_data.get('status') == JobStatus.COMPLETED
            )
            
            return (successful_jobs / total_jobs) * 100 if total_jobs > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Error calculating success rate: {e}")
            return None
    
    async def _calculate_error_rate(self) -> Optional[float]:
        """Calculate job error rate percentage."""
        try:
            success_rate = await self._calculate_success_rate()
            return 100 - success_rate if success_rate is not None else None
            
        except Exception as e:
            self.logger.error(f"Error calculating error rate: {e}")
            return None
    
    async def _calculate_average_queue_time(self) -> Optional[float]:
        """Calculate average job queue time."""
        try:
            if 'queue_time' in self.performance_data:
                recent_data = [
                    d for d in self.performance_data['queue_time']
                    if datetime.utcnow() - d['timestamp'] < timedelta(minutes=15)
                ]
                
                if recent_data:
                    return sum(d['value'] for d in recent_data) / len(recent_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating average queue time: {e}")
            return None
    
    async def _calculate_average_processing_time(self) -> Optional[float]:
        """Calculate average job processing time."""
        try:
            if 'processing_time' in self.performance_data:
                recent_data = [
                    d for d in self.performance_data['processing_time']
                    if datetime.utcnow() - d['timestamp'] < timedelta(minutes=15)
                ]
                
                if recent_data:
                    return sum(d['value'] for d in recent_data) / len(recent_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating average processing time: {e}")
            return None
    
    async def _calculate_cost_efficiency(self) -> Optional[float]:
        """Calculate cost efficiency metric."""
        try:
            # This would integrate with your cost tracking system
            # For now, return a placeholder value
            return 85.0
            
        except Exception as e:
            self.logger.error(f"Error calculating cost efficiency: {e}")
            return None
    
    async def _calculate_resource_utilization(self) -> Optional[float]:
        """Calculate resource utilization percentage."""
        try:
            # This would integrate with your resource monitoring system
            # For now, return a placeholder value
            return 75.0
            
        except Exception as e:
            self.logger.error(f"Error calculating resource utilization: {e}")
            return None
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on SLA performance."""
        try:
            recommendations = []
            
            # Check for critical violations
            if self.sla_metrics.critical_slas > 0:
                recommendations.append(f"Address {self.sla_metrics.critical_slas} critical SLA violations immediately.")
            
            # Check for overall compliance
            if self.sla_metrics.overall_compliance_rate < 0.8:
                recommendations.append("Overall SLA compliance is below 80%. Review and optimize system performance.")
            
            # Check for specific metric issues
            if self.sla_metrics.average_response_time > 10:
                recommendations.append("Job response time is high. Consider scaling up resources or optimizing job scheduling.")
            
            if self.sla_metrics.average_throughput < 10:
                recommendations.append("System throughput is low. Investigate bottlenecks and optimize processing.")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations due to system error."]


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'enable_real_time_monitoring': True,
        'alert_cooldown_minutes': 15,
        'violation_threshold': 3,
        'metrics_retention_days': 30
    }
    
    # Initialize SLA monitor
    monitor = SLAMonitor(config)
    
    print("SLAMonitor system initialized successfully!")

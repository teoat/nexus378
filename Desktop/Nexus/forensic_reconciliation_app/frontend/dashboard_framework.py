"""
Dashboard Framework - User Interface and Visualization Components

This module implements the DashboardFramework class that provides
comprehensive dashboard capabilities for the forensic platform.
"""

import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import asyncio

from ..ai_service.taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class DashboardType(Enum):
    """Types of dashboards."""

    OVERVIEW = "overview"  # Main overview dashboard
    RECONCILIATION = "reconciliation"  # Reconciliation analysis dashboard
    FRAUD_DETECTION = "fraud_detection"  # Fraud detection dashboard
    RISK_ASSESSMENT = "risk_assessment"  # Risk assessment dashboard
    EVIDENCE_ANALYSIS = "evidence_analysis"  # Evidence analysis dashboard
    SYSTEM_MONITORING = "system_monitoring"  # System health dashboard
    USER_MANAGEMENT = "user_management"  # User management dashboard
    CUSTOM = "custom"  # Custom user-defined dashboard


class WidgetType(Enum):
    """Types of dashboard widgets."""

    CHART = "chart"  # Data visualization chart
    TABLE = "table"  # Data table
    METRIC = "metric"  # Key performance indicator
    STATUS = "status"  # Status indicator
    TIMELINE = "timeline"  # Timeline visualization
    MAP = "map"  # Geographic visualization
    ALERT = "alert"  # Alert/notification widget
    CUSTOM = "custom"  # Custom widget


class ChartType(Enum):
    """Types of charts."""

    LINE = "line"  # Line chart
    BAR = "bar"  # Bar chart
    PIE = "pie"  # Pie chart
    SCATTER = "scatter"  # Scatter plot
    AREA = "area"  # Area chart
    HEATMAP = "heatmap"  # Heatmap
    CANDLESTICK = "candlestick"  # Candlestick chart
    GAUGE = "gauge"  # Gauge chart


@dataclass
class DashboardConfig:
    """Configuration for a dashboard."""

    dashboard_id: str
    dashboard_name: str
    dashboard_type: DashboardType
    description: str
    layout: Dict[str, Any]
    refresh_interval: int  # seconds
    is_public: bool
    owner_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WidgetConfig:
    """Configuration for a dashboard widget."""

    widget_id: str
    widget_name: str
    widget_type: WidgetType
    chart_type: Optional[ChartType]
    data_source: str
    position: Dict[str, Any]
    size: Dict[str, Any]
    config: Dict[str, Any]
    is_active: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardData:
    """Data for dashboard widgets."""

    widget_id: str
    data_type: str
    data: Any
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardMetrics:
    """Metrics for dashboard performance."""

    total_dashboards: int
    total_widgets: int
    active_users: int
    average_load_time: float
    data_refresh_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class DashboardFramework:
    """
    Comprehensive dashboard framework system.

    The DashboardFramework is responsible for:
    - Managing dashboard configurations and layouts
    - Handling widget rendering and data visualization
    - Providing real-time data updates and refresh
    - Supporting multiple dashboard types and themes
    - Managing user permissions and access control
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the DashboardFramework."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_refresh_interval = config.get("default_refresh_interval", 30)
        self.max_widgets_per_dashboard = config.get("max_widgets_per_dashboard", 20)
        self.enable_real_time_updates = config.get("enable_real_time_updates", True)
        self.enable_custom_widgets = config.get("enable_custom_widgets", True)

        # Dashboard management
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.dashboard_widgets: Dict[str, List[WidgetConfig]] = defaultdict(list)
        self.dashboard_data: Dict[str, Dict[str, DashboardData]] = defaultdict(dict)

        # Widget management
        self.widgets: Dict[str, WidgetConfig] = {}
        self.widget_renderers: Dict[WidgetType, Callable] = {}

        # User management
        self.user_dashboards: Dict[str, List[str]] = defaultdict(list)
        self.dashboard_permissions: Dict[str, Dict[str, List[str]]] = defaultdict(dict)

        # Performance tracking
        self.total_dashboards_created = 0
        self.total_widgets_created = 0
        self.active_users = 0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Background tasks
        self.data_refresh_task = None
        self.monitoring_task = None

        # Initialize dashboard framework components
        self._initialize_dashboard_framework_components()

        self.logger.info("DashboardFramework initialized successfully")

    async def start(self):
        """Start the DashboardFramework."""
        self.logger.info("Starting DashboardFramework...")

        # Initialize dashboard framework components
        await self._initialize_dashboard_framework_components()

        # Start background tasks
        self.data_refresh_task = asyncio.create_task(self._refresh_dashboard_data())
        self.monitoring_task = asyncio.create_task(self._monitor_dashboard_health())

        self.logger.info("DashboardFramework started successfully")

    async def stop(self):
        """Stop the DashboardFramework."""
        self.logger.info("Stopping DashboardFramework...")

        # Cancel background tasks
        if self.data_refresh_task:
            self.data_refresh_task.cancel()
        if self.monitoring_task:
            self.monitoring_task.cancel()

        self.logger.info("DashboardFramework stopped")

    def _initialize_dashboard_framework_components(self):
        """Initialize dashboard framework components."""
        try:
            # Initialize default dashboards
            self._initialize_default_dashboards()

            # Initialize default widgets
            self._initialize_default_widgets()

            # Initialize widget renderers
            self._initialize_widget_renderers()

            self.logger.info("Dashboard framework components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing dashboard framework components: {e}")

    def _initialize_default_dashboards(self):
        """Initialize default dashboards."""
        try:
            # Overview dashboard
            overview_dashboard = DashboardConfig(
                dashboard_id="overview_dashboard",
                dashboard_name="System Overview",
                dashboard_type=DashboardType.OVERVIEW,
                description="Main system overview dashboard with key metrics and status",
                layout={"type": "grid", "columns": 3, "rows": 4},
                refresh_interval=30,
                is_public=True,
                owner_id="system",
            )

            # Reconciliation dashboard
            reconciliation_dashboard = DashboardConfig(
                dashboard_id="reconciliation_dashboard",
                dashboard_name="Reconciliation Analysis",
                dashboard_type=DashboardType.RECONCILIATION,
                description="Forensic reconciliation analysis and results",
                layout={"type": "grid", "columns": 2, "rows": 3},
                refresh_interval=60,
                is_public=True,
                owner_id="system",
            )

            # Fraud detection dashboard
            fraud_dashboard = DashboardConfig(
                dashboard_id="fraud_detection_dashboard",
                dashboard_name="Fraud Detection",
                dashboard_type=DashboardType.FRAUD_DETECTION,
                description="Fraud detection analysis and alerts",
                layout={"type": "grid", "columns": 2, "rows": 3},
                refresh_interval=60,
                is_public=True,
                owner_id="system",
            )

            # Risk assessment dashboard
            risk_dashboard = DashboardConfig(
                dashboard_id="risk_assessment_dashboard",
                dashboard_name="Risk Assessment",
                dashboard_type=DashboardType.RISK_ASSESSMENT,
                description="Risk assessment and compliance monitoring",
                layout={"type": "grid", "columns": 2, "rows": 3},
                refresh_interval=120,
                is_public=True,
                owner_id="system",
            )

            # Evidence analysis dashboard
            evidence_dashboard = DashboardConfig(
                dashboard_id="evidence_analysis_dashboard",
                dashboard_name="Evidence Analysis",
                dashboard_type=DashboardType.EVIDENCE_ANALYSIS,
                description="Evidence processing and analysis results",
                layout={"type": "grid", "columns": 2, "rows": 3},
                refresh_interval=60,
                is_public=True,
                owner_id="system",
            )

            # System monitoring dashboard
            system_dashboard = DashboardConfig(
                dashboard_id="system_monitoring_dashboard",
                dashboard_name="System Monitoring",
                dashboard_type=DashboardType.SYSTEM_MONITORING,
                description="System health and performance monitoring",
                layout={"type": "grid", "columns": 3, "rows": 2},
                refresh_interval=30,
                is_public=True,
                owner_id="system",
            )

            # Store dashboards
            self.dashboards[overview_dashboard.dashboard_id] = overview_dashboard
            self.dashboards[reconciliation_dashboard.dashboard_id] = (
                reconciliation_dashboard
            )
            self.dashboards[fraud_dashboard.dashboard_id] = fraud_dashboard
            self.dashboards[risk_dashboard.dashboard_id] = risk_dashboard
            self.dashboards[evidence_dashboard.dashboard_id] = evidence_dashboard
            self.dashboards[system_dashboard.dashboard_id] = system_dashboard

            # Update metrics
            self.total_dashboards_created = len(self.dashboards)

            self.logger.info(f"Initialized {len(self.dashboards)} default dashboards")

        except Exception as e:
            self.logger.error(f"Error initializing default dashboards: {e}")

    def _initialize_default_widgets(self):
        """Initialize default dashboard widgets."""
        try:
            # Overview dashboard widgets
            overview_widgets = [
                WidgetConfig(
                    widget_id="system_status_widget",
                    widget_name="System Status",
                    widget_type=WidgetType.STATUS,
                    chart_type=None,
                    data_source="system_status",
                    position={"x": 0, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"show_indicators": True, "refresh_rate": 30},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="active_users_widget",
                    widget_name="Active Users",
                    widget_type=WidgetType.METRIC,
                    chart_type=None,
                    data_source="user_activity",
                    position={"x": 1, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"format": "number", "refresh_rate": 30},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="recent_activity_widget",
                    widget_name="Recent Activity",
                    widget_type=WidgetType.TIMELINE,
                    chart_type=None,
                    data_source="activity_log",
                    position={"x": 2, "y": 0, "w": 1, "h": 2},
                    size={"width": 400, "height": 400},
                    config={"max_items": 50, "refresh_rate": 60},
                    is_active=True,
                ),
            ]

            # Reconciliation dashboard widgets
            reconciliation_widgets = [
                WidgetConfig(
                    widget_id="reconciliation_summary_widget",
                    widget_name="Reconciliation Summary",
                    widget_type=WidgetType.METRIC,
                    chart_type=None,
                    data_source="reconciliation_summary",
                    position={"x": 0, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"format": "summary", "refresh_rate": 60},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="reconciliation_chart_widget",
                    widget_name="Reconciliation Trends",
                    widget_type=WidgetType.CHART,
                    chart_type=ChartType.LINE,
                    data_source="reconciliation_trends",
                    position={"x": 1, "y": 0, "w": 1, "h": 2},
                    size={"width": 400, "height": 400},
                    config={"chart_type": "line", "refresh_rate": 120},
                    is_active=True,
                ),
            ]

            # Fraud detection dashboard widgets
            fraud_widgets = [
                WidgetConfig(
                    widget_id="fraud_alerts_widget",
                    widget_name="Fraud Alerts",
                    widget_type=WidgetType.ALERT,
                    chart_type=None,
                    data_source="fraud_alerts",
                    position={"x": 0, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"max_alerts": 20, "refresh_rate": 30},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="fraud_patterns_widget",
                    widget_name="Fraud Patterns",
                    widget_type=WidgetType.CHART,
                    chart_type=ChartType.HEATMAP,
                    data_source="fraud_patterns",
                    position={"x": 1, "y": 0, "w": 1, "h": 2},
                    size={"width": 400, "height": 400},
                    config={"chart_type": "heatmap", "refresh_rate": 300},
                    is_active=True,
                ),
            ]

            # Risk assessment dashboard widgets
            risk_widgets = [
                WidgetConfig(
                    widget_id="risk_score_widget",
                    widget_name="Risk Score",
                    widget_type=WidgetType.GAUGE,
                    chart_type=ChartType.GAUGE,
                    data_source="risk_scores",
                    position={"x": 0, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 300},
                    config={"chart_type": "gauge", "refresh_rate": 60},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="risk_trends_widget",
                    widget_name="Risk Trends",
                    widget_type=WidgetType.CHART,
                    chart_type=ChartType.AREA,
                    data_source="risk_trends",
                    position={"x": 1, "y": 0, "w": 1, "h": 2},
                    size={"width": 400, "height": 400},
                    config={"chart_type": "area", "refresh_rate": 120},
                    is_active=True,
                ),
            ]

            # Evidence analysis dashboard widgets
            evidence_widgets = [
                WidgetConfig(
                    widget_id="evidence_summary_widget",
                    widget_name="Evidence Summary",
                    widget_type=WidgetType.TABLE,
                    chart_type=None,
                    data_source="evidence_summary",
                    position={"x": 0, "y": 0, "w": 1, "h": 1},
                    size={"width": 400, "height": 300},
                    config={"max_rows": 20, "refresh_rate": 60},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="evidence_processing_widget",
                    widget_name="Processing Status",
                    widget_type=WidgetType.STATUS,
                    chart_type=None,
                    data_source="evidence_processing",
                    position={"x": 1, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"show_progress": True, "refresh_rate": 30},
                    is_active=True,
                ),
            ]

            # System monitoring dashboard widgets
            system_widgets = [
                WidgetConfig(
                    widget_id="cpu_usage_widget",
                    widget_name="CPU Usage",
                    widget_type=WidgetType.CHART,
                    chart_type=ChartType.LINE,
                    data_source="system_metrics",
                    position={"x": 0, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"metric": "cpu", "refresh_rate": 30},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="memory_usage_widget",
                    widget_name="Memory Usage",
                    widget_type=WidgetType.CHART,
                    chart_type=ChartType.LINE,
                    data_source="system_metrics",
                    position={"x": 1, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"metric": "memory", "refresh_rate": 30},
                    is_active=True,
                ),
                WidgetConfig(
                    widget_id="network_traffic_widget",
                    widget_name="Network Traffic",
                    widget_type=WidgetType.CHART,
                    chart_type=ChartType.AREA,
                    data_source="system_metrics",
                    position={"x": 2, "y": 0, "w": 1, "h": 1},
                    size={"width": 300, "height": 200},
                    config={"metric": "network", "refresh_rate": 30},
                    is_active=True,
                ),
            ]

            # Store widgets by dashboard
            self.dashboard_widgets["overview_dashboard"] = overview_widgets
            self.dashboard_widgets["reconciliation_dashboard"] = reconciliation_widgets
            self.dashboard_widgets["fraud_detection_dashboard"] = fraud_widgets
            self.dashboard_widgets["risk_assessment_dashboard"] = risk_widgets
            self.dashboard_widgets["evidence_analysis_dashboard"] = evidence_widgets
            self.dashboard_widgets["system_monitoring_dashboard"] = system_widgets

            # Store all widgets
            for widgets in self.dashboard_widgets.values():
                for widget in widgets:
                    self.widgets[widget.widget_id] = widget

            # Update metrics
            self.total_widgets_created = len(self.widgets)

            self.logger.info(f"Initialized {len(self.widgets)} default widgets")

        except Exception as e:
            self.logger.error(f"Error initializing default widgets: {e}")

    def _initialize_widget_renderers(self):
        """Initialize widget renderers."""
        try:
            # Register widget renderers
            self.widget_renderers[WidgetType.CHART] = self._render_chart_widget
            self.widget_renderers[WidgetType.TABLE] = self._render_table_widget
            self.widget_renderers[WidgetType.METRIC] = self._render_metric_widget
            self.widget_renderers[WidgetType.STATUS] = self._render_status_widget
            self.widget_renderers[WidgetType.TIMELINE] = self._render_timeline_widget
            self.widget_renderers[WidgetType.MAP] = self._render_map_widget
            self.widget_renderers[WidgetType.ALERT] = self._render_alert_widget
            self.widget_renderers[WidgetType.CUSTOM] = self._render_custom_widget

            self.logger.info(
                f"Initialized {len(self.widget_renderers)} widget renderers"
            )

        except Exception as e:
            self.logger.error(f"Error initializing widget renderers: {e}")

    async def create_dashboard(
        self,
        dashboard_name: str,
        dashboard_type: DashboardType,
        description: str,
        owner_id: str,
        layout: Dict[str, Any] = None,
    ) -> str:
        """Create a new dashboard."""
        try:
            dashboard_id = str(uuid.uuid4())

            if layout is None:
                layout = {"type": "grid", "columns": 2, "rows": 2}

            config = DashboardConfig(
                dashboard_id=dashboard_id,
                dashboard_name=dashboard_name,
                dashboard_type=dashboard_type,
                description=description,
                layout=layout,
                refresh_interval=self.default_refresh_interval,
                is_public=False,
                owner_id=owner_id,
            )

            # Store dashboard
            self.dashboards[dashboard_id] = config

            # Initialize widget list
            self.dashboard_widgets[dashboard_id] = []

            # Update user dashboards
            self.user_dashboards[owner_id].append(dashboard_id)

            # Update metrics
            self.total_dashboards_created += 1

            self.logger.info(f"Created dashboard: {dashboard_id} - {dashboard_name}")

            return dashboard_id

        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            raise

    async def add_widget_to_dashboard(
        self,
        dashboard_id: str,
        widget_name: str,
        widget_type: WidgetType,
        data_source: str,
        position: Dict[str, Any],
        size: Dict[str, Any],
        chart_type: Optional[ChartType] = None,
    ) -> str:
        """Add a widget to a dashboard."""
        try:
            # Validate dashboard exists
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} does not exist")

            # Check widget limit
            if (
                len(self.dashboard_widgets[dashboard_id])
                >= self.max_widgets_per_dashboard
            ):
                raise ValueError(
                    f"Dashboard {dashboard_id} has reached maximum widget limit"
                )

            widget_id = str(uuid.uuid4())

            widget = WidgetConfig(
                widget_id=widget_id,
                widget_name=widget_name,
                widget_type=widget_type,
                chart_type=chart_type,
                data_source=data_source,
                position=position,
                size=size,
                config={"refresh_rate": 60},
                is_active=True,
            )

            # Store widget
            self.widgets[widget_id] = widget
            self.dashboard_widgets[dashboard_id].append(widget)

            # Update metrics
            self.total_widgets_created += 1

            self.logger.info(f"Added widget {widget_id} to dashboard {dashboard_id}")

            return widget_id

        except Exception as e:
            self.logger.error(f"Error adding widget to dashboard: {e}")
            raise

    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data and configuration."""
        try:
            # Validate dashboard exists
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} does not exist")

            dashboard = self.dashboards[dashboard_id]
            widgets = self.dashboard_widgets[dashboard_id]

            # Get widget data
            widget_data = {}
            for widget in widgets:
                if widget.is_active:
                    data = await self._get_widget_data(widget)
                    widget_data[widget.widget_id] = data

            return {
                "dashboard": dashboard,
                "widgets": widgets,
                "widget_data": widget_data,
                "layout": dashboard.layout,
                "refresh_interval": dashboard.refresh_interval,
            }

        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            raise

    async def _get_widget_data(self, widget: WidgetConfig) -> Dict[str, Any]:
        """Get data for a specific widget."""
        try:
            # This would integrate with actual data sources
            # For now, return mock data based on widget type

            if widget.widget_type == WidgetType.METRIC:
                return {"value": 42, "unit": "items", "trend": "up", "change": "+5%"}
            elif widget.widget_type == WidgetType.CHART:
                return {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                    "datasets": [{"label": "Data", "data": [10, 20, 15, 25, 30]}],
                }
            elif widget.widget_type == WidgetType.TABLE:
                return {
                    "headers": ["Column 1", "Column 2", "Column 3"],
                    "rows": [
                        ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
                        ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 2"],
                    ],
                }
            elif widget.widget_type == WidgetType.STATUS:
                return {
                    "status": "healthy",
                    "indicators": {
                        "cpu": "normal",
                        "memory": "normal",
                        "network": "normal",
                    },
                }
            else:
                return {"data": "No data available"}

        except Exception as e:
            self.logger.error(f"Error getting widget data: {e}")
            return {"error": str(e)}

    def _render_chart_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a chart widget."""
        try:
            return {
                "type": "chart",
                "chart_type": widget.chart_type.value if widget.chart_type else "line",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering chart widget: {e}")
            return {"error": str(e)}

    def _render_table_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a table widget."""
        try:
            return {
                "type": "table",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering table widget: {e}")
            return {"error": str(e)}

    def _render_metric_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a metric widget."""
        try:
            return {
                "type": "metric",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering metric widget: {e}")
            return {"error": str(e)}

    def _render_status_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a status widget."""
        try:
            return {
                "type": "status",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering status widget: {e}")
            return {"error": str(e)}

    def _render_timeline_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a timeline widget."""
        try:
            return {
                "type": "timeline",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering timeline widget: {e}")
            return {"error": str(e)}

    def _render_map_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a map widget."""
        try:
            return {
                "type": "map",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering map widget: {e}")
            return {"error": str(e)}

    def _render_alert_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render an alert widget."""
        try:
            return {
                "type": "alert",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering alert widget: {e}")
            return {"error": str(e)}

    def _render_custom_widget(
        self, widget: WidgetConfig, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Render a custom widget."""
        try:
            return {
                "type": "custom",
                "data": data,
                "config": widget.config,
                "position": widget.position,
                "size": widget.size,
            }
        except Exception as e:
            self.logger.error(f"Error rendering custom widget: {e}")
            return {"error": str(e)}

    async def _refresh_dashboard_data(self):
        """Refresh dashboard data at configured intervals."""
        while True:
            try:
                # Refresh data for all active dashboards
                for dashboard_id, dashboard in self.dashboards.items():
                    if dashboard.refresh_interval > 0:
                        # Get current time
                        current_time = time.time()

                        # Check if it's time to refresh
                        if hasattr(dashboard, "last_refresh"):
                            if (
                                current_time - dashboard.last_refresh
                                >= dashboard.refresh_interval
                            ):
                                await self._refresh_dashboard(dashboard_id)
                                dashboard.last_refresh = current_time
                        else:
                            # First refresh
                            await self._refresh_dashboard(dashboard_id)
                            dashboard.last_refresh = current_time

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Error refreshing dashboard data: {e}")
                await asyncio.sleep(10)

    async def _refresh_dashboard(self, dashboard_id: str):
        """Refresh a specific dashboard."""
        try:
            widgets = self.dashboard_widgets.get(dashboard_id, [])

            for widget in widgets:
                if widget.is_active:
                    # Get fresh data
                    data = await self._get_widget_data(widget)

                    # Store updated data
                    self.dashboard_data[dashboard_id][widget.widget_id] = DashboardData(
                        widget_id=widget.widget_id,
                        data_type=widget.widget_type.value,
                        data=data,
                        timestamp=datetime.utcnow(),
                    )

            self.logger.debug(f"Refreshed dashboard {dashboard_id}")

        except Exception as e:
            self.logger.error(f"Error refreshing dashboard {dashboard_id}: {e}")

    async def _monitor_dashboard_health(self):
        """Monitor dashboard health and performance."""
        while True:
            try:
                # Check dashboard health
                for dashboard_id, dashboard in self.dashboards.items():
                    widgets = self.dashboard_widgets.get(dashboard_id, [])

                    # Check if dashboard has widgets
                    if not widgets:
                        self.logger.warning(f"Dashboard {dashboard_id} has no widgets")

                    # Check widget health
                    for widget in widgets:
                        if not widget.is_active:
                            self.logger.warning(
                                f"Widget {widget.widget_id} is inactive"
                            )

                await asyncio.sleep(60)  # Monitor every minute

            except Exception as e:
                self.logger.error(f"Error monitoring dashboard health: {e}")
                await asyncio.sleep(60)

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get dashboard performance metrics."""
        return DashboardMetrics(
            total_dashboards=self.total_dashboards_created,
            total_widgets=self.total_widgets_created,
            active_users=self.active_users,
            average_load_time=0.0,  # Not implemented yet
            data_refresh_rate=0.0,  # Not implemented yet
            metadata={
                "dashboard_types": [dt.value for dt in DashboardType],
                "widget_types": [wt.value for wt in WidgetType],
                "chart_types": [ct.value for ct in ChartType],
                "max_widgets_per_dashboard": self.max_widgets_per_dashboard,
                "enable_real_time_updates": self.enable_real_time_updates,
                "enable_custom_widgets": self.enable_custom_widgets,
            },
        )


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "default_refresh_interval": 30,
        "max_widgets_per_dashboard": 20,
        "enable_real_time_updates": True,
        "enable_custom_widgets": True,
    }

    # Initialize dashboard framework
    dashboard_framework = DashboardFramework(config)

    print("DashboardFramework system initialized successfully!")

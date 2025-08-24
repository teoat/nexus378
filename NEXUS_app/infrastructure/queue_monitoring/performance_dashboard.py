#!/usr/bin/env python3
Performance Dashboard for Nexus Platform
Implements real-time and historical data visualization for queue metrics.
Estimated time: 3-4 hours
MCP Status: IMPLEMENTING - Agent: AI_Assistant

import asyncio
import json
import logging
import statistics
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Types of chartsTypes of charts"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    GAUGE = "gauge"
    TABLE = "table"
    HEATMAP = "heatmap"

class TimeRange(Enum):
    """Time range optionsTime range options"""
    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    CUSTOM = "custom"

@dataclass
class DashboardWidget:
    """Dashboard widget configurationDashboard widget configuration"""
    id: str
    name: str
    chart_type: ChartType
    data_source: str
    refresh_interval: int  # seconds
    position: Tuple[int, int]  # x, y coordinates
    size: Tuple[int, int]  # width, height
    config: Dict[str, Any]
    enabled: bool = True

@dataclass
class DashboardConfig:
    """Dashboard configurationDashboard configuration"""
    name: str
    description: str
    widgets: List[DashboardWidget]
    refresh_interval: int = 30
    theme: str = "dark"
    layout: str = "grid"

@dataclass
class ChartData:
    """Chart data structureChart data structure"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class MCPLogger:
    """Model Context Protocol Logger for tracking agent activitiesModel Context Protocol Logger for tracking agent activities"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.agent_activities: Dict[str, List[Dict[str, Any]]] = {}
        self.implementation_locks: Dict[str, str] = {}
    
    def create_session(self, session_id: str, description: str):
        """Create a new MCP sessionCreate a new MCP session"""
        self.sessions[session_id] = {
            "id": session_id,
            "description": description,
            "created": time.time(),
            "status": "active",
            "components_implemented": [],
            "agent_assignments": {}
        }
        logger.info(f"MCP Session created: {session_id} - {description}")
    
    def assign_component(self, session_id: str, agent_id: str, component: str) -> bool:
        """Assign a component to an agent for implementationAssign a component to an agent for implementation"""
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
        """Log start of component implementationLog start of component implementation"""
        if session_id in self.sessions:
            activity = {
                "timestamp": time.time(),
                "agent_id": agent_id,
                "component": component,
                "action": "implementation_start",
                "status": "in_progress"
            }
            
            if agent_id not in self.agent_activities:
                self.agent_activities[agent_id] = []
            self.agent_activities[agent_id].append(activity)
            
            logger.info(f"Agent {agent_id} started implementing {component}")
    
    def log_implementation_complete(
    self,
    session_id: str,
    agent_id: str,
    component: str
)
        """Log completion of component implementationLog completion of component implementation"""
        if session_id in self.sessions:
            if component not in self.sessions[session_id]["components_implemented"]:
                self.sessions[session_id]["components_implemented"].append(component)
            
            activity = {
                "timestamp": time.time(),
                "agent_id": agent_id,
                "component": component,
                "action": "implementation_complete",
                "status": "completed"
            }
            
            if agent_id not in self.agent_activities:
                self.agent_activities[agent_id] = []
            self.agent_activities[agent_id].append(activity)
            
            logger.info(f"Agent {agent_id} completed implementing {component}")

class PerformanceDashboard:
    """Real-time performance dashboard for queue metricsReal-time performance dashboard for queue metrics"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.widget_data: Dict[str, Dict[str, Any]] = {}
        self.refresh_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        self.mcp_logger = MCPLogger()
        
        # Initialize default dashboard
        self._create_default_dashboard()
        
        logger.info("Performance Dashboard initialized with MCP logging")
    
    def start_implementation_session(
    self,
    description: str = "Performance Dashboard Implementation"
)
        """Start a new implementation sessionStart a new implementation session"""
        session_id = str(uuid.uuid4())
        self.mcp_logger.create_session(session_id, description)
        return session_id
    
    def assign_component_for_implementation(self, session_id: str, agent_id: str, component: str) -> bool:
        """Assign a component to an agent for implementationAssign a component to an agent for implementation"""
        return self.mcp_logger.assign_component(session_id, agent_id, component)
    
    def _create_default_dashboard(self):
        """Create default dashboard with common widgetsCreate default dashboard with common widgets"""
        default_widgets = [
            DashboardWidget(
                id="queue_overview",
                name="Queue Overview",
                chart_type=ChartType.TABLE,
                data_source="queue_stats",
                refresh_interval=30,
                position=(0, 0),
                size=(12, 4),
                config={"columns": ["Queue", "Size", "Throughput", "Latency", "Health"]}
            ),
            DashboardWidget(
                id="throughput_trend",
                name="Throughput Trend",
                chart_type=ChartType.LINE,
                data_source="throughput_history",
                refresh_interval=60,
                position=(0, 4),
                size=(6, 4),
                config={"y_axis": "Messages/Second", "time_range": "1h"}
            ),
            DashboardWidget(
                id="latency_distribution",
                name="Latency Distribution",
                chart_type=ChartType.BAR,
                data_source="latency_history",
                refresh_interval=60,
                position=(6, 4),
                size=(6, 4),
                config={"y_axis": "Milliseconds", "buckets": 10}
            ),
            DashboardWidget(
                id="health_gauge",
                name="System Health",
                chart_type=ChartType.GAUGE,
                data_source="health_scores",
                refresh_interval=30,
                position=(0, 8),
                size=(4, 4),
                config={"min": 0, "max": 100, "thresholds": [50, 75, 90]}
            ),
            DashboardWidget(
                id="error_rate",
                name="Error Rate",
                chart_type=ChartType.LINE,
                data_source="error_history",
                refresh_interval=60,
                position=(4, 8),
                size=(8, 4),
                config={"y_axis": "Errors/Second", "time_range": "6h"}
            )
        ]
        
        default_dashboard = DashboardConfig(
            name="Default Dashboard",
            description="Default performance monitoring dashboard",
            widgets=default_widgets,
            refresh_interval=30
        )
        
        self.dashboards["default"] = default_dashboard
        logger.info("Default dashboard created with 5 widgets")
    
    def create_dashboard(
    self,
    name: str,
    description: str,
    widgets: List[DashboardWidget]
)
        """Create a new dashboardCreate a new dashboard"""
        dashboard_id = str(uuid.uuid4())
        
        dashboard = DashboardConfig(
            name=name,
            description=description,
            widgets=widgets,
            refresh_interval=30
        )
        
        self.dashboards[dashboard_id] = dashboard
        logger.info(f"Dashboard '{name}' created with {len(widgets)} widgets")
        
        return dashboard_id
    
    def add_widget(self, dashboard_id: str, widget: DashboardWidget):
        """Add a widget to a dashboardAdd a widget to a dashboard"""
        if dashboard_id in self.dashboards:
            self.dashboards[dashboard_id].widgets.append(widget)
            logger.info(f"Widget '{widget.name}' added to dashboard '{dashboard_id}'")
        else:
            logger.error(f"Dashboard '{dashboard_id}' not found")
    
    def remove_widget(self, dashboard_id: str, widget_id: str):
        """Remove a widget from a dashboardRemove a widget from a dashboard"""
        if dashboard_id in self.dashboards:
            dashboard = self.dashboards[dashboard_id]
            dashboard.widgets = [w for w in dashboard.widgets if w.id != widget_id]
            logger.info(f"Widget '{widget_id}' removed from dashboard '{dashboard_id}'")
        else:
            logger.error(f"Dashboard '{dashboard_id}' not found")
    
    async def start_dashboard(self, dashboard_id: str):
        """Start a dashboard with automatic refreshStart a dashboard with automatic refresh"""
        if dashboard_id not in self.dashboards:
            logger.error(f"Dashboard '{dashboard_id}' not found")
            return
        
        if dashboard_id in self.refresh_tasks:
            logger.warning(f"Dashboard '{dashboard_id}' is already running")
            return
        
        dashboard = self.dashboards[dashboard_id]
        self.refresh_tasks[dashboard_id] = asyncio.create_task(
            self._dashboard_refresh_loop(dashboard_id, dashboard.refresh_interval)
        )
        
        logger.info(
    f"Dashboard '{dashboard.name}' started with {dashboard.refresh_interval}s refresh",
)
    
    def stop_dashboard(self, dashboard_id: str):
        """Stop a dashboardStop a dashboard"""
        if dashboard_id in self.refresh_tasks:
            self.refresh_tasks[dashboard_id].cancel()
            del self.refresh_tasks[dashboard_id]
            logger.info(f"Dashboard '{dashboard_id}' stopped")
        else:
            logger.warning(f"Dashboard '{dashboard_id}' is not running")
    
    async def _dashboard_refresh_loop(self, dashboard_id: str, refresh_interval: int):
        """Dashboard refresh loopDashboard refresh loop"""
        while True:
            try:
                await asyncio.sleep(refresh_interval)
                await self._refresh_dashboard_data(dashboard_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dashboard refresh loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _refresh_dashboard_data(self, dashboard_id: str):
        """Refresh data for all widgets in a dashboardRefresh data for all widgets in a dashboard"""
        if dashboard_id not in self.dashboards:
            return
        
        dashboard = self.dashboards[dashboard_id]
        
        for widget in dashboard.widgets:
            if widget.enabled:
                try:
                    data = await self._get_widget_data(widget)
                    self.widget_data[widget.id] = data
                except Exception as e:
                    logger.error(f"Error refreshing widget {widget.id}: {e}")
        
        logger.debug(f"Dashboard '{dashboard_id}' data refreshed")
    
    async def _get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for a specific widgetGet data for a specific widget"""
        if widget.data_source == "queue_stats":
            return await self._get_queue_stats_data(widget)
        elif widget.data_source == "throughput_history":
            return await self._get_throughput_history_data(widget)
        elif widget.data_source == "latency_history":
            return await self._get_latency_history_data(widget)
        elif widget.data_source == "health_scores":
            return await self._get_health_scores_data(widget)
        elif widget.data_source == "error_history":
            return await self._get_error_history_data(widget)
        else:
            return {"error": f"Unknown data source: {widget.data_source}"}
    
    async def _get_queue_stats_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get queue statistics data for table widgetGet queue statistics data for table widget"""
        if not self.metrics_collector:
            return {"error": "Metrics collector not available"}
        
        stats = self.metrics_collector.get_all_queue_stats()
        
        table_data = []
        for stat in stats:
            table_data.append({
                "Queue": stat.queue_name,
                "Size": stat.current_size,
                "Throughput": f"{stat.avg_throughput:.2f}",
                "Latency": f"{stat.avg_latency:.2f}",
                "Health": f"{stat.health_score:.1f}"
            })
        
        return {
            "type": "table",
            "data": table_data,
            "columns": widget.config.get("columns", ["Queue", "Size", "Throughput", "Latency", "Health"]),
            "timestamp": time.time()
        }
    
    async def _get_throughput_history_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get throughput history data for line chartGet throughput history data for line chart"""
        if not self.metrics_collector:
            return {"error": "Metrics collector not available"}
        
        # Simulate historical throughput data
        time_range = widget.config.get("time_range", "1h")
        data_points = self._get_time_points(time_range)
        
        datasets = []
        for queue_name in ["main_queue", "processing_queue", "archive_queue"]:
            values = (
    [max(0.1, (hash(f"{queue_name}_{i}") % 100) / 10.0) for i in range(len(data_points))]
)
            datasets.append({
                "label": queue_name,
                "data": values,
                "borderColor": self._get_queue_color(queue_name),
                "fill": False
            })
        
        return {
            "type": "line",
            "labels": data_points,
            "datasets": datasets,
            "options": {
                "y_axis": widget.config.get("y_axis", "Messages/Second"),
                "time_range": time_range
            },
            "timestamp": time.time()
        }
    
    async def _get_latency_history_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get latency history data for bar chartGet latency history data for bar chart"""
        if not self.metrics_collector:
            return {"error": "Metrics collector not available"}
        
        # Simulate historical latency data
        buckets = widget.config.get("buckets", 10)
        bucket_labels = [f"{i*10}-{(i+1)*10}ms" for i in range(buckets)]
        
        datasets = []
        for queue_name in ["main_queue", "processing_queue", "archive_queue"]:
            values = [hash(f"{queue_name}_{i}") % 100 for i in range(buckets)]
            datasets.append({
                "label": queue_name,
                "data": values,
                "backgroundColor": self._get_queue_color(queue_name, alpha=0.7),
                "borderColor": self._get_queue_color(queue_name),
                "borderWidth": 1
            })
        
        return {
            "type": "bar",
            "labels": bucket_labels,
            "datasets": datasets,
            "options": {
                "y_axis": widget.config.get("y_axis", "Milliseconds"),
                "buckets": buckets
            },
            "timestamp": time.time()
        }
    
    async def _get_health_scores_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get health scores data for gauge widgetGet health scores data for gauge widget"""
        if not self.metrics_collector:
            return {"error": "Metrics collector not available"}
        
        stats = self.metrics_collector.get_all_queue_stats()
        overall_health = (
    sum(stat.health_score for stat in stats) / len(stats) if stats else 0
)
        
        return {
            "type": "gauge",
            "value": overall_health,
            "min": widget.config.get("min", 0),
            "max": widget.config.get("max", 100),
            "thresholds": widget.config.get("thresholds", [50, 75, 90]),
            "unit": "%",
            "timestamp": time.time()
        }
    
    async def _get_error_history_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get error history data for line chartGet error history data for line chart"""
        if not self.metrics_collector:
            return {"error": "Metrics collector not available"}
        
        # Simulate historical error data
        time_range = widget.config.get("time_range", "6h")
        data_points = self._get_time_points(time_range)
        
        datasets = []
        for queue_name in ["main_queue", "processing_queue", "archive_queue"]:
            values = (
    [max(0, (hash(f"{queue_name}_{i}") % 10) / 100.0) for i in range(len(data_points))]
)
            datasets.append({
                "label": queue_name,
                "data": values,
                "borderColor": self._get_queue_color(queue_name),
                "fill": False
            })
        
        return {
            "type": "line",
            "labels": data_points,
            "datasets": datasets,
            "options": {
                "y_axis": widget.config.get("y_axis", "Errors/Second"),
                "time_range": time_range
            },
            "timestamp": time.time()
        }
    
    def _get_time_points(self, time_range: str) -> List[str]:
        """Get time points for charts based on time rangeGet time points for charts based on time range"""
        now = datetime.now()
        
        if time_range == "1h":
            points = 60
            interval = timedelta(minutes=1)
        elif time_range == "6h":
            points = 72
            interval = timedelta(minutes=5)
        elif time_range == "24h":
            points = 96
            interval = timedelta(minutes=15)
        elif time_range == "7d":
            points = 168
            interval = timedelta(hours=1)
        elif time_range == "30d":
            points = 30
            interval = timedelta(days=1)
        else:
            points = 60
            interval = timedelta(minutes=1)
        
        time_points = []
        for i in range(points):
            time_point = now - (interval * (points - i - 1))
            time_points.append(time_point.strftime("%H:%M") if time_range in ["1h", "6h"] else time_point.strftime("%m/%d"))
        
        return time_points
    
    def _get_queue_color(self, queue_name: str, alpha: float = 1.0) -> str:
        """Get consistent color for a queueGet consistent color for a queue"""
        colors = {
            "main_queue": f"rgba(54, 162, 235, {alpha})",
            "processing_queue": f"rgba(255, 99, 132, {alpha})",
            "archive_queue": f"rgba(75, 192, 192, {alpha})"
        }
        return colors.get(queue_name, f"rgba(128, 128, 128, {alpha})")
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get current data for a dashboardGet current data for a dashboard"""
        if dashboard_id not in self.dashboards:
            return {"error": "Dashboard not found"}
        
        dashboard = self.dashboards[dashboard_id]
        dashboard_data = {
            "id": dashboard_id,
            "name": dashboard.name,
            "description": dashboard.description,
            "theme": dashboard.theme,
            "layout": dashboard.layout,
            "widgets": []
        }
        
        for widget in dashboard.widgets:
            widget_data = {
                "id": widget.id,
                "name": widget.name,
                "type": widget.chart_type.value,
                "position": widget.position,
                "size": widget.size,
                "config": widget.config,
                "enabled": widget.enabled,
                "data": self.widget_data.get(widget.id, {})
            }
            dashboard_data["widgets"].append(widget_data)
        
        return dashboard_data
    
    def export_dashboard_config(self, dashboard_id: str) -> str:
        """Export dashboard configuration as JSONExport dashboard configuration as JSON"""
        if dashboard_id not in self.dashboards:
            return json.dumps({"error": "Dashboard not found"})
        
        dashboard = self.dashboards[dashboard_id]
        return json.dumps(asdict(dashboard), indent=2, default=str)
    
    def import_dashboard_config(self, config_json: str) -> str:
        """Import dashboard configuration from JSONImport dashboard configuration from JSON"""
        try:
            config_data = json.loads(config_json)
            
            # Convert widgets back to objects
            widgets = []
            for widget_data in config_data.get("widgets", []):
                widget = DashboardWidget(
                    id=widget_data["id"],
                    name=widget_data["name"],
                    chart_type=ChartType(widget_data["chart_type"]),
                    data_source=widget_data["data_source"],
                    refresh_interval=widget_data["refresh_interval"],
                    position=tuple(widget_data["position"]),
                    size=tuple(widget_data["size"]),
                    config=widget_data["config"],
                    enabled=widget_data.get("enabled", True)
                )
                widgets.append(widget)
            
            dashboard = DashboardConfig(
                name=config_data["name"],
                description=config_data["description"],
                widgets=widgets,
                refresh_interval=config_data.get("refresh_interval", 30),
                theme=config_data.get("theme", "dark"),
                layout=config_data.get("layout", "grid")
            )
            
            dashboard_id = str(uuid.uuid4())
            self.dashboards[dashboard_id] = dashboard
            
            logger.info(f"Dashboard '{dashboard.name}' imported successfully")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to import dashboard config: {e}")
            return ""
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary of all dashboardsGet summary of all dashboards"""
        summary = {
            "total_dashboards": len(self.dashboards),
            "running_dashboards": len(self.refresh_tasks),
            "total_widgets": sum(len(d.widgets) for d in self.dashboards.values()),
            "dashboards": {}
        }
        
        for dashboard_id, dashboard in self.dashboards.items():
            summary["dashboards"][dashboard_id] = {
                "name": dashboard.name,
                "description": dashboard.description,
                "widgets": len(dashboard.widgets),
                "running": dashboard_id in self.refresh_tasks,
                "refresh_interval": dashboard.refresh_interval
            }
        
        return summary

# Example usage and testing
def test_performance_dashboard():
    """Test the Performance Dashboard with MCP loggingTest the Performance Dashboard with MCP logging"""
    print("🧪 Testing Performance Dashboard with MCP Logging")
    print("=" * 60)
    
    # Create dashboard
    dashboard = PerformanceDashboard()
    
    # Start implementation session
    session_id = dashboard.start_implementation_session("Performance Dashboard Testing")
    print(f"📋 MCP Session created: {session_id}")
    
    # Assign component to agent
    agent_id = "AI_Assistant"
    component = "performance_dashboard"
    
    if dashboard.assign_component_for_implementation(session_id, agent_id, component):
        print(f"✅ Component {component} assigned to {agent_id}")
        
        # Log implementation start
        dashboard.mcp_logger.log_implementation_start(session_id, agent_id, component)
        
        # List dashboards
        print("\n📊 Available Dashboards:")
        summary = dashboard.get_dashboard_summary()
        print(f"  Total Dashboards: {summary['total_dashboards']}")
        print(f"  Running Dashboards: {summary['running_dashboards']}")
        print(f"  Total Widgets: {summary['total_widgets']}")
        
        # Get default dashboard data
        print("\n📈 Default Dashboard Data:")
        default_data = dashboard.get_dashboard_data("default")
        print(f"  Dashboard: {default_data['name']}")
        print(f"  Widgets: {len(default_data['widgets'])}")
        
        for widget in default_data['widgets']:
            print(f"    - {widget['name']} ({widget['type']})")
        
        # Export dashboard config
        print("\n💾 Exporting Dashboard Config:")
        config_json = dashboard.export_dashboard_config("default")
        print(f"  Config exported: {len(config_json)} characters")
        
        # Log implementation complete
        dashboard.mcp_logger.log_implementation_complete(session_id, agent_id, component)
        
        print("\n✅ Performance Dashboard test completed!")
        
    else:
        print(f"❌ Failed to assign component {component}")

if __name__ == "__main__":
    # Run the test
    test_performance_dashboard()

Dashboard Framework - User Interface and Visualization Components

This module implements the DashboardFramework class that provides
comprehensive dashboard capabilities for the forensic platform.

import logging
import time
import uuid
from datetime import datetime, timedelta

import asyncio
import aiohttp

from ..ai_service.taskmaster.models.job import Job, JobPriority, JobStatus, JobType

class DashboardType(Enum):

    OVERVIEW = "overview"  # Main overview dashboard
    RECONCILIATION = "reconciliation"  # Reconciliation analysis dashboard
    FRAUD_DETECTION = "fraud_detection"  # Fraud detection dashboard
    RISK_ASSESSMENT = "risk_assessment"  # Risk assessment dashboard
    EVIDENCE_ANALYSIS = "evidence_analysis"  # Evidence analysis dashboard
    SYSTEM_MONITORING = "system_monitoring"  # System health dashboard
    USER_MANAGEMENT = "user_management"  # User management dashboard
    CUSTOM = "custom"  # Custom user-defined dashboard

class WidgetType(Enum):

    CHART = "chart"  # Data visualization chart
    TABLE = "table"  # Data table
    METRIC = "metric"  # Key performance indicator
    STATUS = "status"  # Status indicator
    TIMELINE = "timeline"  # Timeline visualization
    MAP = "map"  # Geographic visualization
    ALERT = "alert"  # Alert/notification widget
    CUSTOM = "custom"  # Custom widget

class ChartType(Enum):

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

            raise RuntimeError("API session not initialized")

        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                async with self.session.request(
                    method, url, json=data, params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise Exception("Authentication failed")
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        response.raise_for_status()
                        
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    raise e
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
        
        raise Exception("Max retry attempts exceeded")

    async def get_reconciliation_data(self, source_data: List[Dict], target_data: List[Dict]) -> Dict[str, Any]:

                "source_data": source_data,
                "target_data": target_data,
                "confidence_threshold": 0.8,
                "matching_fields": ["id", "name", "amount"]
            }
            
            result = await self._make_request("POST", "/api/v1/reconcile", data=payload)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get reconciliation data: {e}")
            return {"error": str(e)}

    async def get_fraud_detection_data(self, transaction_data: List[Dict]) -> Dict[str, Any]:

                "transaction_data": transaction_data,
                "risk_threshold": 0.7
            }
            
            result = await self._make_request("POST", "/api/v1/fraud-detect", data=payload)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get fraud detection data: {e}")
            return {"error": str(e)}

    async def get_nlp_data(self, text: str) -> Dict[str, Any]:

                "text": text,
                "language": "en",
                "tasks": ["entities", "sentiment", "keywords", "summary"]
            }
            
            result = await self._make_request("POST", "/api/v1/nlp", data=payload)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get NLP data: {e}")
            return {"error": str(e)}

    async def get_ocr_data(self, document_data: bytes, document_type: str) -> Dict[str, Any]:

                "document_data": document_data.decode('latin-1'),  # Simple encoding for demo
                "document_type": document_type,
                "language": "en"
            }
            
            result = await self._make_request("POST", "/api/v1/ocr", data=payload)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get OCR data: {e}")
            return {"error": str(e)}

    async def get_system_health(self) -> Dict[str, Any]:

            result = await self._make_request("GET", "/health")
            return result
        except Exception as e:
            self.logger.error(f"Failed to get system health: {e}")
            return {"error": str(e)}

    async def get_metrics(self) -> Dict[str, Any]:

            result = await self._make_request("GET", "/metrics")
            return result
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}

class DashboardFramework:

        self.default_refresh_interval = self.config.get("default_refresh_interval", 30)
        self.max_widgets_per_dashboard = self.config.get("max_widgets_per_dashboard", 20)
        self.enable_real_time_updates = self.config.get("enable_real_time_updates", True)
        self.enable_custom_widgets = self.config.get("enable_custom_widgets", True)
        
        # API integration
        api_config = APIConfig(
            base_url=self.config.get("api_base_url", "http://localhost:8001"),
            api_key=self.config.get("api_key"),
            timeout=self.config.get("api_timeout", 30)
        )
        self.api_integration = APIIntegration(api_config)
        
        # Statistics
        self.total_dashboards_created = 0
        self.total_widgets_created = 0
        self.active_users = 0
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._refresh_task = None
        self._health_monitor_task = None
        self._running = False

    async def start(self):

        self.logger.info("Dashboard framework started")

    async def stop(self):

        self.logger.info("Dashboard framework stopped")

    async def create_dashboard(
        self,
        name: str,
        dashboard_type: DashboardType,
        description: str = "",
        owner_id: str = "default",
        is_public: bool = True,
        layout: Optional[Dict[str, Any]] = None,
        refresh_interval: Optional[int] = None
    ) -> str:

            layout=layout or {"grid": "12x12"},
            refresh_interval=refresh_interval or self.default_refresh_interval,
            is_public=is_public,
            owner_id=owner_id
        )
        
        self.dashboards[dashboard_id] = dashboard_config
        self.total_dashboards_created += 1
        
        self.logger.info(f"Created dashboard: {name} ({dashboard_id})")
        return dashboard_id

    async def add_widget(
        self,
        dashboard_id: str,
        name: str,
        widget_type: WidgetType,
        data_source: str,
        position: Dict[str, Any],
        size: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        chart_type: Optional[ChartType] = None
    ) -> str:

            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        if len(self.dashboard_widgets[dashboard_id]) >= self.max_widgets_per_dashboard:
            raise ValueError(f"Dashboard {dashboard_id} has reached maximum widget limit")
        
        widget_id = str(uuid.uuid4())
        
        widget_config = WidgetConfig(
            widget_id=widget_id,
            widget_name=name,
            widget_type=widget_type,
            chart_type=chart_type,
            data_source=data_source,
            position=position,
            size=size,
            config=config or {},
            is_active=True
        )
        
        self.dashboard_widgets[dashboard_id].append(widget_config)
        self.total_widgets_created += 1
        
        self.logger.info(f"Added widget {name} to dashboard {dashboard_id}")
        return widget_id

    async def _get_widget_data(self, widget: WidgetConfig) -> Any:

            if widget.data_source.startswith("api://"):
                # API data source
                endpoint = widget.data_source.replace("api://", "")
                return await self._get_api_data(endpoint, widget.config)
            elif widget.data_source.startswith("mock://"):
                # Mock data for testing
                return self._get_mock_data(widget.data_source, widget.config)
            else:
                # Default to mock data
                return self._get_mock_data("mock://default", widget.config)
                
        except Exception as e:
            self.logger.error(f"Error getting widget data: {e}")
            return {"error": str(e)}

    async def _get_api_data(self, endpoint: str, config: Dict[str, Any]) -> Any:

                if endpoint == "reconciliation":
                    source_data = config.get("source_data", [])
                    target_data = config.get("target_data", [])
                    return await api.get_reconciliation_data(source_data, target_data)
                elif endpoint == "fraud_detection":
                    transaction_data = config.get("transaction_data", [])
                    return await api.get_fraud_detection_data(transaction_data)
                elif endpoint == "nlp":
                    text = config.get("text", "")
                    return await api.get_nlp_data(text)
                elif endpoint == "ocr":
                    document_data = config.get("document_data", b"")
                    document_type = config.get("document_type", "unknown")
                    return await api.get_ocr_data(document_data, document_type)
                elif endpoint == "health":
                    return await api.get_system_health()
                elif endpoint == "metrics":
                    return await api.get_metrics()
                else:
                    return {"error": f"Unknown endpoint: {endpoint}"}
                    
        except Exception as e:
            self.logger.error(f"API data fetch error: {e}")
            return {"error": str(e)}

    def _get_mock_data(self, data_source: str, config: Dict[str, Any]) -> Any:

        if data_source == "mock://reconciliation":
            return {
                "matches": [
                    {"source_id": "S001", "target_id": "T001", "confidence": 0.95},
                    {"source_id": "S002", "target_id": "T002", "confidence": 0.87}
                ],
                "unmatched_source": ["S003", "S004"],
                "unmatched_target": ["T003", "T004"]
            }
        elif data_source == "mock://fraud_detection":
            return {
                "fraud_scores": [0.2, 0.8, 0.1, 0.9],
                "risk_levels": ["low", "high", "low", "high"],
                "flagged_transactions": [1, 3]
            }
        elif data_source == "mock://nlp":
            return {
                "entities": ["John Doe", "Company Inc", "New York"],
                "sentiment": {"positive": 0.6, "negative": 0.2, "neutral": 0.2},
                "keywords": ["forensic", "analysis", "investigation"]
            }
        else:
            return {"message": "Mock data", "timestamp": datetime.utcnow().isoformat()}

    async def _refresh_dashboards(self):

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

            self.logger.debug(f"Refreshed dashboard {dashboard_id}")

        except Exception as e:
            self.logger.error(f"Error refreshing dashboard {dashboard_id}: {e}")

    async def _monitor_dashboard_health(self):

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
        "api_base_url": "http://localhost:8001",
        "api_timeout": 30
    }

    # Initialize dashboard framework
    dashboard_framework = DashboardFramework(config)

    print("DashboardFramework system initialized successfully!")
    print("API integration enabled for backend services")

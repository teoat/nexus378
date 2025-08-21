"""
Resource Monitor for Taskmaster System
Monitors system health and resource usage
"""

import asyncio
import logging
import psutil
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int

class ResourceMonitor:
    """Resource monitoring system for Taskmaster"""
    
    def __init__(self):
        self.is_monitoring = False
        self.metrics_history: List[SystemMetrics] = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0
        }
        
        logger.info("Resource Monitor initialized")
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        logger.info("Starting resource monitoring")
        
        # Start monitoring task
        asyncio.create_task(self._monitor_system_resources())
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_monitoring = False
        logger.info("Resource monitoring stopped")
    
    async def _monitor_system_resources(self):
        """Monitor system resources continuously"""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self._check_alerts(metrics)
                self.metrics_history.append(metrics)
                
                # Keep only last 100 metrics
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring system resources: {e}")
                await asyncio.sleep(15)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            try:
                connections = len(psutil.net_connections())
            except:
                connections = 0
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                active_connections=connections
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                active_connections=0
            )
    
    def _check_alerts(self, metrics: SystemMetrics):
        """Check if metrics exceed alert thresholds"""
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            logger.warning(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            logger.warning(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.disk_percent > self.alert_thresholds['disk_percent']:
            logger.warning(f"High disk usage: {metrics.disk_percent:.1f}%")
    
    def get_system_summary(self) -> Dict:
        """Get current system status summary"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest = self.metrics_history[-1]
        return {
            "status": "monitoring",
            "current": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_percent": latest.disk_percent,
                "active_connections": latest.active_connections
            }
        }

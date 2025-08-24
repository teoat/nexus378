#!/usr/bin/env python3
Queue Metrics Collection for Nexus Platform
Implements comprehensive queue monitoring and metrics collection.
Estimated time: 2-3 hours
MCP Status: IMPLEMENTING - Agent: AI_Assistant

import asyncio
import json
import logging
import statistics
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metricsTypes of metrics"""
    QUEUE_SIZE = "queue_size"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    CONSUMER_COUNT = "consumer_count"
    PRODUCER_COUNT = "producer_count"
    PROCESSING_TIME = "processing_time"
    WAIT_TIME = "wait_time"

@dataclass
class QueueMetric:
    """Individual metric data pointIndividual metric data point"""
    id: str
    queue_name: str
    metric_type: MetricType
    value: float
    timestamp: float
    tags: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class QueueStats:
    """Queue statistics summaryQueue statistics summary"""
    queue_name: str
    current_size: int
    total_messages: int
    avg_throughput: float
    avg_latency: float
    error_rate: float
    consumer_count: int
    producer_count: int
    last_updated: float
    health_score: float

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

class QueueMetricsCollector:
    """Collects and manages queue metricsCollects and manages queue metrics"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.queue_stats: Dict[str, QueueStats] = {}
        self.collection_task = None
        self.is_collecting = False
        self.mcp_logger = MCPLogger()
        
        logger.info("Queue Metrics Collector initialized with MCP logging")
    
    def start_implementation_session(
    self,
    description: str = "Queue Metrics Implementation"
)
        """Start a new implementation sessionStart a new implementation session"""
        session_id = str(uuid.uuid4())
        self.mcp_logger.create_session(session_id, description)
        return session_id
    
    def assign_component_for_implementation(self, session_id: str, agent_id: str, component: str) -> bool:
        """Assign a component to an agent for implementationAssign a component to an agent for implementation"""
        return self.mcp_logger.assign_component(session_id, agent_id, component)
    
    def record_metric(self, queue_name: str, metric_type: MetricType, value: float, 
                     tags: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record a new metricRecord a new metric"""
        metric = QueueMetric(
            id=str(uuid.uuid4()),
            queue_name=queue_name,
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        key = f"{queue_name}_{metric_type.value}"
        self.metrics[key].append(metric)
        
        # Update queue stats
        self._update_queue_stats(queue_name, metric_type, value)
        
        logger.debug(f"Recorded metric: {queue_name} {metric_type.value} = {value}")
    
    def record_queue_size(self, queue_name: str, size: int):
        """Record queue size metricRecord queue size metric"""
        self.record_metric(queue_name, MetricType.QUEUE_SIZE, float(size))
    
    def record_throughput(self, queue_name: str, messages_per_second: float):
        """Record throughput metricRecord throughput metric"""
        self.record_metric(queue_name, MetricType.THROUGHPUT, messages_per_second)
    
    def record_latency(self, queue_name: str, latency_ms: float):
        """Record latency metricRecord latency metric"""
        self.record_metric(queue_name, MetricType.LATENCY, latency_ms)
    
    def record_error(self, queue_name: str, error_count: int):
        """Record error metricRecord error metric"""
        self.record_metric(queue_name, MetricType.ERROR_RATE, float(error_count))
    
    def record_consumer_count(self, queue_name: str, count: int):
        """Record consumer count metricRecord consumer count metric"""
        self.record_metric(queue_name, MetricType.CONSUMER_COUNT, float(count))
    
    def record_producer_count(self, queue_name: str, count: int):
        """Record producer count metricRecord producer count metric"""
        self.record_metric(queue_name, MetricType.PRODUCER_COUNT, float(count))
    
    def get_metric(self, queue_name: str, metric_type: MetricType, 
                   time_window_minutes: int = 60) -> List[QueueMetric]:
        """Get metrics for a specific queue and type within time windowGet metrics for a specific queue and type within time window"""
        key = f"{queue_name}_{metric_type.value}"
        if key not in self.metrics:
            return []
        
        cutoff_time = time.time() - (time_window_minutes * 60)
        return [m for m in self.metrics[key] if m.timestamp >= cutoff_time]
    
    def get_metric_history(self, queue_name: str, metric_type: MetricType, 
                          limit: int = 100) -> List[QueueMetric]:
        """Get metric history for a specific queue and typeGet metric history for a specific queue and type"""
        key = f"{queue_name}_{metric_type.value}"
        if key not in self.metrics:
            return []
        
        return list(self.metrics[key])[-limit:]
    
    def get_queue_stats(self, queue_name: str) -> Optional[QueueStats]:
        """Get current statistics for a queueGet current statistics for a queue"""
        return self.queue_stats.get(queue_name)
    
    def get_all_queue_stats(self) -> List[QueueStats]:
        """Get statistics for all queuesGet statistics for all queues"""
        return list(self.queue_stats.values())
    
    def calculate_queue_health_score(self, queue_name: str) -> float:
        """Calculate health score for a queue (0-100)Calculate health score for a queue (0-100)"""
        stats = self.queue_stats.get(queue_name)
        if not stats:
            return 0.0
        
        # Calculate health score based on multiple factors
        size_score = (
    max(0, 100 - (stats.current_size / 1000) * 100)  # Penalize large queues
)
        throughput_score = (
    min(100, (stats.avg_throughput / 100) * 100)  # Reward high throughput
)
        latency_score = (
    max(0, 100 - (stats.avg_latency / 1000) * 100)  # Penalize high latency
)
        error_score = max(0, 100 - stats.error_rate * 100)  # Penalize errors
        
        # Weighted average
        health_score = (size_score * 0.2 + throughput_score * 0.3 + 
                       latency_score * 0.3 + error_score * 0.2)
        
        return min(100.0, max(0.0, health_score))
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metricsGet summary of all metrics"""
        summary = {
            "total_queues": len(self.queue_stats),
            "total_metrics": sum(len(metrics) for metrics in self.metrics.values()),
            "collection_active": self.is_collecting,
            "queues": {}
        }
        
        for queue_name, stats in self.queue_stats.items():
            summary["queues"][queue_name] = {
                "current_size": stats.current_size,
                "health_score": stats.health_score,
                "avg_throughput": stats.avg_throughput,
                "avg_latency": stats.avg_latency,
                "error_rate": stats.error_rate
            }
        
        return summary
    
    def export_metrics_prometheus(self) -> str:
        """Export metrics in Prometheus formatExport metrics in Prometheus format"""
        prometheus_lines = []
        
        for queue_name, stats in self.queue_stats.items():
            # Queue size
            prometheus_lines.append(
    f'queue_size{{queue="{queue_name}"}} {stats.current_size}',
)
            
            # Throughput
            prometheus_lines.append(
    f'queue_throughput{{queue="{queue_name}"}} {stats.avg_throughput}',
)
            
            # Latency
            prometheus_lines.append(
    f'queue_latency{{queue="{queue_name}"}} {stats.avg_latency}',
)
            
            # Error rate
            prometheus_lines.append(
    f'queue_error_rate{{queue="{queue_name}"}} {stats.error_rate}',
)
            
            # Health score
            prometheus_lines.append(
    f'queue_health_score{{queue="{queue_name}"}} {stats.health_score}',
)
        
        return '\n'.join(prometheus_lines)
    
    def export_metrics_json(self) -> str:
        """Export metrics in JSON formatExport metrics in JSON format"""
        return json.dumps(self.get_metrics_summary(), indent=2, default=str)
    
    async def start_collection(self, interval_seconds: int = 60):
        """Start automatic metric collectionStart automatic metric collection"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_task = (
    asyncio.create_task(self._collection_loop(interval_seconds))
)
        logger.info(f"Started metric collection with {interval_seconds}s interval")
    
    def stop_collection(self):
        """Stop automatic metric collectionStop automatic metric collection"""
        if not self.is_collecting:
            return
        
        self.is_collecting = False
        if self.collection_task:
            self.collection_task.cancel()
        logger.info("Stopped metric collection")
    
    async def _collection_loop(self, interval_seconds: int):
        """Metric collection loopMetric collection loop"""
        while self.is_collecting:
            try:
                await asyncio.sleep(interval_seconds)
                
                if self.is_collecting:
                    await self._collect_system_metrics()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _collect_system_metrics(self):
        """Collect system-level metricsCollect system-level metrics"""
        try:
            # Simulate system metrics collection
            for queue_name in self.queue_stats.keys():
                # Simulate queue size changes
                current_size = self.queue_stats[queue_name].current_size
                new_size = max(0, current_size + (hash(queue_name) % 10) - 5)
                self.record_queue_size(queue_name, new_size)
                
                # Simulate throughput changes
                throughput = max(0.1, (hash(queue_name) % 100) / 10.0)
                self.record_throughput(queue_name, throughput)
                
                # Simulate latency changes
                latency = max(1.0, (hash(queue_name) % 1000) / 10.0)
                self.record_latency(queue_name, latency)
            
            logger.debug("Collected system metrics")
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def cleanup_old_metrics(self):
        """Clean up old metrics based on retention policyClean up old metrics based on retention policy"""
        cutoff_time = time.time() - (self.retention_hours * 3600)
        
        for key, metrics in self.metrics.items():
            # Remove old metrics
            while metrics and metrics[0].timestamp < cutoff_time:
                metrics.popleft()
        
        logger.info("Cleaned up old metrics")
    
    def _update_queue_stats(
    self,
    queue_name: str,
    metric_type: MetricType,
    value: float
)
        """Update queue statisticsUpdate queue statistics"""
        if queue_name not in self.queue_stats:
            self.queue_stats[queue_name] = QueueStats(
                queue_name=queue_name,
                current_size=0,
                total_messages=0,
                avg_throughput=0.0,
                avg_latency=0.0,
                error_rate=0.0,
                consumer_count=0,
                producer_count=0,
                last_updated=time.time(),
                health_score=100.0
            )
        
        stats = self.queue_stats[queue_name]
        stats.last_updated = time.time()
        
        # Update specific metrics
        if metric_type == MetricType.QUEUE_SIZE:
            stats.current_size = int(value)
        elif metric_type == MetricType.THROUGHPUT:
            # Calculate running average
            if stats.avg_throughput == 0:
                stats.avg_throughput = value
            else:
                stats.avg_throughput = (stats.avg_throughput * 0.9) + (value * 0.1)
        elif metric_type == MetricType.LATENCY:
            # Calculate running average
            if stats.avg_latency == 0:
                stats.avg_latency = value
            else:
                stats.avg_latency = (stats.avg_latency * 0.9) + (value * 0.1)
        elif metric_type == MetricType.ERROR_RATE:
            stats.error_rate = value
        elif metric_type == MetricType.CONSUMER_COUNT:
            stats.consumer_count = int(value)
        elif metric_type == MetricType.PRODUCER_COUNT:
            stats.producer_count = int(value)
        
        # Update health score
        stats.health_score = self.calculate_queue_health_score(queue_name)

# Example usage and testing
def test_queue_metrics():
    """Test the Queue Metrics Collector with MCP loggingTest the Queue Metrics Collector with MCP logging"""
    print("🧪 Testing Queue Metrics Collector with MCP Logging")
    print("=" * 60)
    
    # Create metrics collector
    collector = QueueMetricsCollector()
    
    # Start implementation session
    session_id = collector.start_implementation_session("Queue Metrics Testing")
    print(f"📋 MCP Session created: {session_id}")
    
    # Assign component to agent
    agent_id = "AI_Assistant"
    component = "queue_metrics_collection"
    
    if collector.assign_component_for_implementation(session_id, agent_id, component):
        print(f"✅ Component {component} assigned to {agent_id}")
        
        # Log implementation start
        collector.mcp_logger.log_implementation_start(session_id, agent_id, component)
        
        # Record some test metrics
        print("\n📊 Recording test metrics...")
        collector.record_queue_size("test_queue", 150)
        collector.record_throughput("test_queue", 25.5)
        collector.record_latency("test_queue", 45.2)
        collector.record_error("test_queue", 0.02)
        collector.record_consumer_count("test_queue", 3)
        collector.record_producer_count("test_queue", 2)
        
        # Get queue stats
        print("\n📈 Queue Statistics:")
        stats = collector.get_queue_stats("test_queue")
        if stats:
            print(f"  Queue: {stats.queue_name}")
            print(f"  Current Size: {stats.current_size}")
            print(f"  Avg Throughput: {stats.avg_throughput:.2f} msg/s")
            print(f"  Avg Latency: {stats.avg_latency:.2f} ms")
            print(f"  Error Rate: {stats.error_rate:.3f}")
            print(f"  Health Score: {stats.health_score:.1f}/100")
        
        # Get metrics summary
        print("\n📊 Metrics Summary:")
        summary = collector.get_metrics_summary()
        print(f"  Total Queues: {summary['total_queues']}")
        print(f"  Total Metrics: {summary['total_metrics']}")
        print(f"  Collection Active: {summary['collection_active']}")
        
        # Export metrics
        print("\n📤 Exporting metrics...")
        prometheus_metrics = collector.export_metrics_prometheus()
        print(f"  Prometheus format: {len(prometheus_metrics.split(chr(10)))} lines")
        
        json_metrics = collector.export_metrics_json()
        print(f"  JSON format: {len(json_metrics)} characters")
        
        # Log implementation complete
        collector.mcp_logger.log_implementation_complete(session_id, agent_id, component)
        
        print("\n✅ Queue Metrics test completed!")
        
    else:
        print(f"❌ Failed to assign component {component}")

if __name__ == "__main__":
    # Run the test
    test_queue_metrics()

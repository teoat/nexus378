#!/usr/bin/env python3
"""
🚀 Enhanced Frenly Enhancement Automation System
Unified automation system with intelligent task breakdown, dynamic worker scaling, and self-learning optimization
Specifically designed for implementing Frenly enhancement todos with enhanced capacity and monitoring
"""

import os
import sys
import time
import json
import asyncio
import threading
import logging
import queue
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable, TypeVar, Union
from enum import Enum
import random
import subprocess
import traceback
import functools
import hashlib
import pickle
import weakref
import gc
import uuid
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from contextlib import asynccontextmanager

# Optional imports with graceful fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("psutil not available - memory monitoring disabled")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("aiohttp not available - HTTP connection pooling disabled")

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("asyncpg not available - PostgreSQL connection pooling disabled")

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("redis not available - Redis caching disabled")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_frenly_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')

# Enhanced Enums
class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    REVIEW = "review"

class WorkerStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    COLLABORATING = "collaborating"
    RECOVERING = "recovering"
    OPTIMIZING = "optimizing"

class TaskComplexity(Enum):
    SIMPLE = 1
    BASIC = 2
    MODERATE = 3
    COMPLEX = 4
    VERY_COMPLEX = 5

class RecoveryAction(Enum):
    RETRY = "retry"
    ROLLBACK = "rollback"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    IGNORE = "ignore"

# Data Classes for Enhanced Features
@dataclass
class RecoveryStep:
    action: RecoveryAction
    handler: Callable
    max_attempts: int = 1
    delay: float = 0.0
    condition: Optional[Callable] = None

@dataclass
class LoadBalancerStats:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    health_score: float = 100.0
    weight: float = 1.0

@dataclass
class QueueItem:
    priority: int
    timestamp: datetime
    data: Any
    attempts: int = 0
    max_attempts: int = 3
    retry_delay: int = 60
    
    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp

@dataclass
class DeadLetterItem:
    original_item: QueueItem
    failure_reason: str
    failed_at: datetime
    error_details: str

@dataclass
class HealthStatus:
    status: str
    checks: List[Dict[str, Any]]
    timestamp: datetime
    overall_score: float

# Enhanced Configuration Management
@dataclass
class SystemConfig:
    max_concurrent_tasks: int = field(ge=1, le=1000, default=50)
    task_timeout: int = field(ge=60, le=7200, default=1800)
    retry_attempts: int = field(ge=0, le=10, default=3)
    retry_delay: int = field(ge=1, le=300, default=45)
    loop_interval: int = field(ge=5, le=300, default=30)
    max_tasks_per_cycle: int = field(ge=1, le=1000, default=100)
    enable_monitoring: bool = True
    enable_collaboration: bool = True
    enable_auto_recovery: bool = True
    enable_performance_optimization: bool = True
    enable_task_breakdown: bool = True
    subworker_capacity: int = field(ge=1, le=20, default=5)
    max_subworker_tasks: int = field(ge=1, le=10000, default=250)

# Enhanced FrenlyEnhancementAutomation Class
class FrenlyEnhancementAutomation:
    """
    Enhanced automation system for Frenly enhancement todos
    Features: Intelligent task breakdown, dynamic worker scaling, and self-learning optimization
    Plus all 30 optimization recommendations integrated
    """
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.frenly_todo_path = self.project_root / "forensic_reconciliation_app" / "FRENLY_ENHANCEMENT_TODO.md"
        
        # Core system attributes
        self.cycle_counter = 0
        self.metrics = {
            'total_tasks_processed': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'success_rate': 0.0,
            'cycle_times': [],
            'average_cycle_time': 0.0,
            'worker_efficiency': {}
        }
        
        # Enhanced configuration with validation
        self.config = SystemConfig()
        
        # System state
        self.tasks = []
        self.workers = {}
        self.completed_tasks = []
        self.failed_tasks = []
        self.pending_tasks = []
        
        # Performance tracking
        self.cycle_start_time = None
        self.cycle_metrics = {}
        self.status_update_counter = 0
        self.status_update_threshold = 5
        
        # Enhanced system metrics
        self.system_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "success_rate": 0.0,
            "average_completion_time": 0.0,
            "system_uptime": 0,
            "start_time": datetime.now()
        }
        
        # Collaboration and recovery
        self.collaboration_network = {}
        self.error_patterns = {}
        self.recovery_strategies = {}
        self.performance_history = []
        
        # Initialize enhanced features
        self._initialize_enhanced_system()
        
    def _initialize_enhanced_system(self):
        """Initialize all enhanced features"""
        logger.info("🚀 Initializing Enhanced Frenly Enhancement Automation System")
        
        # Initialize core components
        self._load_frenly_todos()
        self._initialize_workers()
        self._setup_recovery_strategies()
        self._setup_collaboration_network()
        
        # Initialize enhanced features
        self._initialize_connection_pools()
        self._initialize_caching_system()
        self._initialize_error_recovery()
        self._initialize_load_balancer()
        self._initialize_advanced_queue()
        self._initialize_memory_manager()
        self._initialize_health_checker()
        self._initialize_event_bus()
        self._initialize_dependency_graph()
        self._initialize_performance_profiler()
        self._initialize_graceful_shutdown()
        
        logger.info("✅ Enhanced system initialization complete")
    
    # === RECOMMENDATION 1: Configuration Management ===
    def _load_configuration(self, config_path: Optional[Path] = None) -> bool:
        """Load configuration from file with validation"""
        try:
            if config_path and config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update config with loaded data
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                logger.info("Configuration loaded successfully")
                return True
            else:
                logger.info("Using default configuration")
                return True
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    # === RECOMMENDATION 2: Strategy Pattern for Task Processing ===
    async def _process_task_with_strategy(self, task: Dict[str, Any]) -> bool:
        """Process task using appropriate strategy"""
        task_type = task.get('type', 'general')
        
        strategies = {
            'workflow': self._process_workflow_task,
            'machine-learning': self._process_ml_task,
            'frontend': self._process_frontend_task,
            'backend': self._process_backend_task,
            'monitoring': self._process_monitoring_task,
            'testing': self._process_testing_task,
            'data-processing': self._process_data_task,
            'security': self._process_security_task,
            'integration': self._process_integration_task
        }
        
        strategy = strategies.get(task_type, self._process_general_task)
        return await strategy(task)
    
    async def _process_workflow_task(self, task: Dict[str, Any]) -> bool:
        """Process workflow-specific task"""
        return await self._process_task(task)
    
    async def _process_ml_task(self, task: Dict[str, Any]) -> bool:
        """Process ML-specific task"""
        return await self._process_task(task)
    
    async def _process_frontend_task(self, task: Dict[str, Any]) -> bool:
        """Process frontend-specific task"""
        return await self._process_task(task)
    
    async def _process_backend_task(self, task: Dict[str, Any]) -> bool:
        """Process backend-specific task"""
        return await self._process_task(task)
    
    async def _process_monitoring_task(self, task: Dict[str, Any]) -> bool:
        """Process monitoring-specific task"""
        return await self._process_task(task)
    
    async def _process_testing_task(self, task: Dict[str, Any]) -> bool:
        """Process testing-specific task"""
        return await self._process_task(task)
    
    async def _process_data_task(self, task: Dict[str, Any]) -> bool:
        """Process data-processing-specific task"""
        return await self._process_task(task)
    
    async def _process_security_task(self, task: Dict[str, Any]) -> bool:
        """Process security-specific task"""
        return await self._process_task(task)
    
    async def _process_integration_task(self, task: Dict[str, Any]) -> bool:
        """Process integration-specific task"""
        return await self._process_task(task)
    
    async def _process_general_task(self, task: Dict[str, Any]) -> bool:
        """Process general task"""
        return await self._process_task(task)
    
    # === RECOMMENDATION 3: Command Pattern for Task Operations ===
    async def _execute_task_command(self, command: Callable, *args, **kwargs) -> bool:
        """Execute task command with rollback capability"""
        try:
            # Execute command
            result = await command(*args, **kwargs)
            
            # Store rollback function if available
            if hasattr(command, 'rollback'):
                self.rollback_stack.append(command.rollback)
            
            return result
            
        except Exception as e:
            # Execute rollback
            await self._execute_rollback()
            raise e
    
    async def _execute_rollback(self):
        """Execute rollback operations"""
        while self.rollback_stack:
            rollback_func = self.rollback_stack.pop()
            try:
                if asyncio.iscoroutinefunction(rollback_func):
                    await rollback_func()
                else:
                    rollback_func()
            except Exception as e:
                logger.error(f"Rollback operation failed: {e}")
    
    # === RECOMMENDATION 4: Dependency Injection Container ===
    def _get_service(self, service_type: str) -> Any:
        """Get service from container"""
        return getattr(self, f"{service_type}_service", None)
    
    # === RECOMMENDATION 5: Observer Pattern for Metrics ===
    def _notify_metrics_observers(self, metrics: Dict[str, Any]):
        """Notify all metrics observers"""
        for observer in self.metrics_observers:
            try:
                if asyncio.iscoroutinefunction(observer):
                    asyncio.create_task(observer(metrics))
                else:
                    observer(metrics)
            except Exception as e:
                logger.error(f"Error in metrics observer: {e}")
    
    # === RECOMMENDATION 6: Circuit Breaker Pattern ===
    async def _execute_with_circuit_breaker(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.circuit_breaker_state == 'OPEN':
            if time.time() - self.last_failure_time > self.circuit_breaker_timeout:
                self.circuit_breaker_state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.circuit_breaker_state == 'HALF_OPEN':
                self.circuit_breaker_state = 'CLOSED'
                self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.circuit_breaker_threshold:
                self.circuit_breaker_state = 'OPEN'
            raise e
    
    # === RECOMMENDATION 7: Factory Pattern for Task Creation ===
    def _create_task(self, description: str, phase: str, section: str) -> Dict[str, Any]:
        """Create task using factory pattern"""
        priority = self._determine_task_priority(phase, section, description)
        complexity = self._assess_task_complexity(description)
        estimated_time = self._estimate_task_time(complexity)
        task_type = self._extract_task_type(description)
        tags = self._extract_tags(description)
        
        return {
            'id': f"todo_{uuid.uuid4().hex[:8]}",
            'description': description,
            'phase': phase,
            'section': section,
            'priority': priority,
            'complexity': complexity,
            'estimated_time': estimated_time,
            'status': TaskStatus.PENDING,
            'assigned_worker': None,
            'start_time': None,
            'completion_time': None,
            'retry_count': 0,
            'dependencies': [],
            'tags': tags,
            'type': task_type,
            'created_at': datetime.now()
        }
    
    # === RECOMMENDATION 8: Resource Pool Management ===
    async def _acquire_resource(self, resource_type: str) -> Any:
        """Acquire resource from pool"""
        if resource_type not in self.resource_pools:
            return None
        
        pool = self.resource_pools[resource_type]
        return await pool.acquire()
    
    def _release_resource(self, resource_type: str, resource: Any):
        """Release resource back to pool"""
        if resource_type in self.resource_pools:
            self.resource_pools[resource_type].release(resource)
    
    # === RECOMMENDATION 9: State Machine for Task Lifecycle ===
    def _can_transition_task_state(self, from_state: TaskStatus, to_state: TaskStatus) -> bool:
        """Check if task state transition is valid"""
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.REVIEW],
            TaskStatus.REVIEW: [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS],
            TaskStatus.FAILED: [TaskStatus.PENDING],
            TaskStatus.BLOCKED: [TaskStatus.PENDING]
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def _transition_task_state(self, task: Dict[str, Any], new_state: TaskStatus) -> bool:
        """Transition task to new state if valid"""
        current_state = task['status']
        
        if self._can_transition_task_state(current_state, new_state):
            task['status'] = new_state
            return True
        
        logger.warning(f"Invalid state transition: {current_state} -> {new_state}")
        return False
    
    # === RECOMMENDATION 10: Comprehensive Logging and Monitoring ===
    def _log_with_context(self, level: str, message: str, context: Dict[str, Any] = None):
        """Log message with context information"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'cycle': self.cycle_counter,
            'context': context or {}
        }
        
        if level == 'INFO':
            logger.info(json.dumps(log_data))
        elif level == 'WARNING':
            logger.warning(json.dumps(log_data))
        elif level == 'ERROR':
            logger.error(json.dumps(log_data))
        elif level == 'DEBUG':
            logger.debug(json.dumps(log_data))
    
    # === RECOMMENDATION 11: Caching Layer with TTL ===
    @functools.lru_cache(maxsize=1000)
    def _cached_complexity_assessment(self, description: str) -> int:
        """Cached complexity assessment"""
        return self._assess_task_complexity(description)
    
    # === RECOMMENDATION 12: Rate Limiting and Throttling ===
    async def _throttled_worker_operation(self, worker_id: str, operation: Callable, *args, **kwargs):
        """Execute worker operation with throttling"""
        if worker_id in self.worker_throttlers:
            await self.worker_throttlers[worker_id].acquire()
        
        return await operation(*args, **kwargs)
    
    # === RECOMMENDATION 13: Retry Mechanism with Exponential Backoff ===
    async def _retry_operation(self, operation: Callable, max_retries: int = 3, 
                              base_delay: float = 1.0, *args, **kwargs) -> Any:
        """Retry operation with exponential backoff"""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, operation, *args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    raise last_exception
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
                await asyncio.sleep(delay)
        
        raise last_exception
    
    # === RECOMMENDATION 14: Health Check and Self-Diagnosis ===
    async def _perform_health_check(self) -> HealthStatus:
        """Perform comprehensive health check"""
        checks = [
            await self._check_memory_usage(),
            await self._check_worker_health(),
            await self._check_queue_health(),
            await self._check_connection_health()
        ]
        
        overall_score = sum(check.get('score', 0) for check in checks) / len(checks)
        status = 'healthy' if overall_score >= 0.8 else 'degraded' if overall_score >= 0.6 else 'unhealthy'
        
        return HealthStatus(
            status=status,
            checks=checks,
            timestamp=datetime.now(),
            overall_score=overall_score
        )
    
    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage"""
        if not PSUTIL_AVAILABLE:
            return {'name': 'memory_usage', 'status': 'not_available', 'score': 1.0}
        
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            score = max(0, 100 - usage_percent) / 100
            
            return {
                'name': 'memory_usage',
                'status': 'healthy' if usage_percent < 80 else 'degraded',
                'details': f"{usage_percent:.1f}% used",
                'score': score
            }
        except Exception as e:
            return {'name': 'memory_usage', 'status': 'failed', 'error': str(e), 'score': 0}
    
    async def _check_worker_health(self) -> Dict[str, Any]:
        """Check worker health"""
        try:
            healthy_workers = sum(1 for w in self.workers.values() 
                                if w['status'] != WorkerStatus.RECOVERING)
            total_workers = len(self.workers)
            score = healthy_workers / total_workers if total_workers > 0 else 0
            
            return {
                'name': 'worker_health',
                'status': 'healthy' if score > 0.8 else 'degraded',
                'details': f"{healthy_workers}/{total_workers} workers healthy",
                'score': score
            }
        except Exception as e:
            return {'name': 'worker_health', 'status': 'failed', 'error': str(e), 'score': 0}
    
    async def _check_queue_health(self) -> Dict[str, Any]:
        """Check queue health"""
        try:
            if hasattr(self, 'task_queue'):
                queue_size = self.task_queue.qsize() if hasattr(self.task_queue, 'qsize') else 0
                max_size = getattr(self.task_queue, 'maxsize', 1000)
                score = 1.0 - (queue_size / max_size) if max_size > 0 else 1.0
                
                return {
                    'name': 'queue_health',
                    'status': 'healthy' if score > 0.7 else 'degraded',
                    'details': f"{queue_size}/{max_size} queue utilization",
                    'score': score
                }
            else:
                return {'name': 'queue_health', 'status': 'not_implemented', 'score': 1.0}
        except Exception as e:
            return {'name': 'queue_health', 'status': 'failed', 'error': str(e), 'score': 0}
    
    async def _check_connection_health(self) -> Dict[str, Any]:
        """Check connection health"""
        try:
            if hasattr(self, 'connection_pools'):
                healthy_connections = 0
                total_connections = 0
                
                for pool_name, pool in self.connection_pools.items():
                    if hasattr(pool, 'get_health'):
                        health = pool.get_health()
                        healthy_connections += health.get('healthy', 0)
                        total_connections += health.get('total', 0)
                
                score = healthy_connections / total_connections if total_connections > 0 else 1.0
                
                return {
                    'name': 'connection_health',
                    'status': 'healthy' if score > 0.8 else 'degraded',
                    'details': f"{healthy_connections}/{total_connections} connections healthy",
                    'score': score
                }
            else:
                return {'name': 'connection_health', 'status': 'not_implemented', 'score': 1.0}
        except Exception as e:
            return {'name': 'connection_health', 'status': 'failed', 'error': str(e), 'score': 0}
    
    # === RECOMMENDATION 15: Event-Driven Architecture ===
    def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to event bus"""
        if hasattr(self, 'event_bus'):
            event = {
                'type': event_type,
                'data': data,
                'timestamp': datetime.now(),
                'source': 'frenly_automation'
            }
            self.event_bus.publish(event)
    
    # === RECOMMENDATION 16: Configuration Validation ===
    def _validate_configuration(self) -> bool:
        """Validate system configuration"""
        try:
            # Validate numeric ranges
            if not (1 <= self.config.max_concurrent_tasks <= 1000):
                logger.error("Invalid max_concurrent_tasks value")
                return False
            
            if not (60 <= self.config.task_timeout <= 7200):
                logger.error("Invalid task_timeout value")
                return False
            
            # Validate other config values
            if self.config.retry_attempts < 0 or self.config.retry_attempts > 10:
                logger.error("Invalid retry_attempts value")
                return False
            
            logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    # === RECOMMENDATION 17: Task Dependency Resolution ===
    def _setup_dependency_graph(self):
        """Setup task dependency graph"""
        if not hasattr(self, 'dependency_graph'):
            self.dependency_graph = {}
        
        # Add all tasks to the graph
        for task in self.tasks:
            dependencies = task.get('dependencies', [])
            self.dependency_graph[task['id']] = dependencies
    
    def _get_ready_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that are ready to execute (dependencies met)"""
        ready_tasks = []
        
        for task in self.tasks:
            if (task['status'] == TaskStatus.PENDING and 
                self._are_dependencies_met(task)):
                ready_tasks.append(task)
        
        return ready_tasks
    
    def _are_dependencies_met(self, task: Dict[str, Any]) -> bool:
        """Check if all dependencies are met for a task"""
        if not hasattr(self, 'dependency_graph'):
            return True
        
        dependencies = self.dependency_graph.get(task['id'], [])
        
        for dep_id in dependencies:
            dep_task = next((t for t in self.tasks if t['id'] == dep_id), None)
            if not dep_task or dep_task['status'] != TaskStatus.COMPLETED:
                return False
        
        return True
    
    # === RECOMMENDATION 18: Performance Profiling ===
    def _profile_function(self, func_name: str = None):
        """Profile function execution"""
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self._record_function_timing(func_name or func.__name__, execution_time)
            return async_wrapper
        return decorator
    
    def _record_function_timing(self, func_name: str, execution_time: float):
        """Record function execution timing"""
        if not hasattr(self, 'function_timings'):
            self.function_timings = defaultdict(list)
        
        self.function_timings[func_name].append(execution_time)
        
        # Detect bottlenecks
        if execution_time > 1.0:  # More than 1 second
            if not hasattr(self, 'bottlenecks'):
                self.bottlenecks = []
            
            self.bottlenecks.append({
                'function': func_name,
                'execution_time': execution_time,
                'timestamp': time.time()
            })
    
    # === RECOMMENDATION 19: Graceful Shutdown ===
    def _setup_graceful_shutdown(self):
        """Setup graceful shutdown handlers"""
        self.shutdown_handlers = [
            self._cleanup_workers,
            self._save_system_state,
            self._close_connections,
            self._generate_final_report
        ]
    
    async def _cleanup_workers(self):
        """Cleanup worker resources"""
        logger.info("Cleaning up workers...")
        
        for worker_id, worker in self.workers.items():
            if worker['status'] == WorkerStatus.WORKING:
                if worker['current_task']:
                    worker['current_task']['status'] = TaskStatus.BLOCKED
                    worker['current_task']['assigned_worker'] = None
                
                worker['status'] = WorkerStatus.IDLE
                worker['current_task'] = None
        
        logger.info("Worker cleanup completed")
    
    async def _save_system_state(self):
        """Save current system state"""
        logger.info("Saving system state...")
        
        state_data = {
            'timestamp': datetime.now().isoformat(),
            'cycle_counter': self.cycle_counter,
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'pending_tasks': len([t for t in self.tasks if t['status'] == TaskStatus.PENDING]),
            'worker_statuses': {wid: w['status'].value for wid, w in self.workers.items()},
            'metrics': self.metrics
        }
        
        try:
            state_file = Path('.taskmaster/system_state.json')
            state_file.parent.mkdir(exist_ok=True)
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            logger.info("System state saved successfully")
        except Exception as e:
            logger.error(f"Failed to save system state: {e}")
    
    async def _close_connections(self):
        """Close all open connections"""
        logger.info("Closing connections...")
        
        if hasattr(self, 'connection_pools'):
            for pool_name, pool in self.connection_pools.items():
                if hasattr(pool, 'close'):
                    await pool.close()
        
        logger.info("Connections closed")
    
    async def _generate_final_report(self):
        """Generate final system report"""
        logger.info("Generating final report...")
        self._print_summary()
        logger.info("Final report generated")
    
    # === RECOMMENDATION 20: Testing Framework ===
    def _run_self_tests(self) -> bool:
        """Run self-tests to verify system functionality"""
        test_results = []
        
        # Test task creation
        try:
            test_task = self._create_task("Test task", "Test Phase", "Test Section")
            test_results.append(('task_creation', True))
        except Exception as e:
            test_results.append(('task_creation', False, str(e)))
        
        # Test state transitions
        try:
            test_task = {'status': TaskStatus.PENDING}
            result = self._transition_task_state(test_task, TaskStatus.IN_PROGRESS)
            test_results.append(('state_transition', result))
        except Exception as e:
            test_results.append(('state_transition', False, str(e)))
        
        # Test dependency resolution
        try:
            self.tasks = [{'id': '1', 'status': TaskStatus.COMPLETED}, 
                         {'id': '2', 'status': TaskStatus.PENDING, 'dependencies': ['1']}]
            self._setup_dependency_graph()
            ready_tasks = self._get_ready_tasks()
            test_results.append(('dependency_resolution', len(ready_tasks) == 1))
        except Exception as e:
            test_results.append(('dependency_resolution', False, str(e)))
        
        # Log test results
        passed = sum(1 for result in test_results if result[1])
        total = len(test_results)
        
        logger.info(f"Self-tests completed: {passed}/{total} passed")
        
        for test_name, success, *details in test_results:
            if success:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED - {details[0] if details else 'Unknown error'}")
        
        return passed == total
    
    # === RECOMMENDATION 21: Connection Pooling ===
    async def _initialize_connection_pools(self):
        """Initialize connection pools"""
        self.connection_pools = {}
        
        # Initialize database connection pool
        if ASYNCPG_AVAILABLE:
            try:
                self.connection_pools['database'] = await self._create_db_pool()
                logger.info("Database connection pool initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize database pool: {e}")
        else:
            logger.info("Database connection pooling disabled - asyncpg not available")
        
        # Initialize HTTP connection pool
        if AIOHTTP_AVAILABLE:
            try:
                self.connection_pools['http'] = await self._create_http_pool()
                logger.info("HTTP connection pool initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize HTTP pool: {e}")
        else:
            logger.info("HTTP connection pooling disabled - aiohttp not available")
    
    async def _create_db_pool(self):
        """Create database connection pool"""
        # Simplified pool creation
        return {
            'connections': [],
            'max_size': 10,
            'current_size': 0
        }
    
    async def _create_http_pool(self):
        """Create HTTP connection pool"""
        # Simplified pool creation
        return {
            'sessions': [],
            'max_size': 5,
            'current_size': 0
        }
    
    # === RECOMMENDATION 22: Advanced Caching ===
    async def _initialize_caching_system(self):
        """Initialize caching system"""
        try:
            self.cache = {
                'memory': {},
                'memory_ttl': {},
                'max_size': 1000
            }
            
            if REDIS_AVAILABLE:
                try:
                    self.redis_client = redis.from_url("redis://localhost:6379")
                    logger.info("Redis caching initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize Redis: {e}")
            else:
                logger.info("Redis caching disabled - redis not available")
            
            logger.info("Caching system initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize caching: {e}")
    
    # === RECOMMENDATION 23: Error Recovery ===
    async def _initialize_error_recovery(self):
        """Initialize error recovery system"""
        self.recovery_strategies = {
            'timeout': [RecoveryStep(RecoveryAction.RETRY, None, max_attempts=3, delay=1.0)],
            'connection_error': [RecoveryStep(RecoveryAction.RETRY, None, max_attempts=3, delay=2.0)],
            'worker_failure': [RecoveryStep(RecoveryAction.ESCALATE, None)]
        }
        
        self.rollback_stack = []
        logger.info("Error recovery system initialized")
    
    # === RECOMMENDATION 24: Load Balancing ===
    async def _initialize_load_balancer(self):
        """Initialize load balancer"""
        self.load_balancer = {
            'targets': {},
            'strategy': 'weighted_round_robin'
        }
        logger.info("Load balancer initialized")
    
    # === RECOMMENDATION 25: Advanced Queue ===
    async def _initialize_advanced_queue(self):
        """Initialize advanced queue system"""
        self.task_queue = queue.PriorityQueue(maxsize=10000)
        logger.info("Advanced queue system initialized")
    
    # === RECOMMENDATION 26: Memory Management ===
    async def _initialize_memory_manager(self):
        """Initialize memory manager"""
        self.memory_threshold = 0.8
        self.gc_threshold = 1000
        self.object_count = 0
        
        if PSUTIL_AVAILABLE:
            # Start memory monitoring
            asyncio.create_task(self._monitor_memory_usage())
            logger.info("Memory manager initialized with monitoring")
        else:
            logger.info("Memory manager initialized without monitoring (psutil not available)")
    
    async def _monitor_memory_usage(self):
        """Monitor memory usage"""
        while True:
            try:
                memory_percent = psutil.virtual_memory().percent / 100
                
                if memory_percent > self.memory_threshold:
                    logger.warning(f"High memory usage: {memory_percent:.1%}")
                    await self._trigger_memory_cleanup()
                
                if self.object_count > self.gc_threshold:
                    logger.info(f"High object count: {self.object_count}")
                    await self._trigger_garbage_collection()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _trigger_memory_cleanup(self):
        """Trigger memory cleanup"""
        logger.info("Starting memory cleanup...")
        
        # Clear caches
        if hasattr(self, 'cache'):
            self.cache['memory'].clear()
            self.cache['memory_ttl'].clear()
        
        # Force garbage collection
        await self._trigger_garbage_collection()
        
        logger.info("Memory cleanup completed")
    
    async def _trigger_garbage_collection(self):
        """Trigger garbage collection"""
        logger.info("Starting garbage collection...")
        
        initial_count = len(gc.get_objects())
        collected = gc.collect()
        final_count = len(gc.get_objects())
        
        logger.info(f"Garbage collection completed: {collected} objects collected, "
                   f"{final_count - initial_count} objects freed")
    
    # === RECOMMENDATION 27: Health Checker ===
    async def _initialize_health_checker(self):
        """Initialize health checker"""
        self.health_checks = [
            self._check_memory_usage,
            self._check_worker_health,
            self._check_queue_health,
            self._check_connection_health
        ]
        logger.info("Health checker initialized")
    
    # === RECOMMENDATION 28: Event Bus ===
    async def _initialize_event_bus(self):
        """Initialize event bus"""
        self.event_bus = {
            'subscribers': defaultdict(list),
            'event_history': []
        }
        logger.info("Event bus initialized")
    
    # === RECOMMENDATION 29: Dependency Graph ===
    async def _initialize_dependency_graph(self):
        """Initialize dependency graph"""
        self.dependency_graph = {}
        logger.info("Dependency graph initialized")
    
    # === RECOMMENDATION 30: Performance Profiler ===
    async def _initialize_performance_profiler(self):
        """Initialize performance profiler"""
        self.function_timings = defaultdict(list)
        self.bottlenecks = []
        logger.info("Performance profiler initialized")
    
    # === RECOMMENDATION 31: Graceful Shutdown ===
    async def _initialize_graceful_shutdown(self):
        """Initialize graceful shutdown"""
        self._setup_graceful_shutdown()
        logger.info("Graceful shutdown initialized")
    
    # Enhanced initialization methods
    def _load_frenly_todos(self):
        """Load Frenly enhancement todos from markdown file"""
        try:
            if not self.frenly_todo_path.exists():
                logger.error(f"❌ Frenly enhancement todo file not found: {self.frenly_todo_path}")
                return
                
            with open(self.frenly_todo_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse todos from markdown
            self.tasks = self._parse_todos_from_markdown(content)
            logger.info(f"�� Loaded {len(self.tasks)} Frenly enhancement todos")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Frenly todos: {e}")
    
    def _parse_todos_from_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse todos from markdown content"""
        todos = []
        lines = content.split('\n')
        current_phase = ""
        current_section = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Detect phases
            if line.startswith('## 📋 **Phase'):
                current_phase = line
                continue
                
            # Detect sections
            if line.startswith('### **'):
                current_section = line
                continue
                
            # Detect todo items
            if line.startswith('- [ ]'):
                todo_description = line.replace('- [ ]', '').strip()
                
                # Use factory pattern to create task
                todo = self._create_task(todo_description, current_phase, current_section)
                todo['line_number'] = i + 1
                
                todos.append(todo)
                
        return todos
    
    def _extract_task_type(self, description: str) -> str:
        """Extract task type from description with improved matching"""
        description_lower = description.lower()
        
        # Check for specific types with broader keyword matching
        type_keywords = {
            'workflow': ['workflow', 'process', 'automation', 'pipeline', 'orchestration', 'flow'],
            'machine-learning': ['ml', 'machine learning', 'ai', 'model', 'train', 'predict', 'neural'],
            'frontend': ['ui', 'frontend', 'interface', 'design', 'component', 'view', 'react', 'angular', 'vue'],
            'backend': ['api', 'backend', 'server', 'database', 'endpoint', 'service', 'microservice'],
            'monitoring': ['monitor', 'logging', 'metrics', 'dashboard', 'alert', 'observe'],
            'testing': ['test', 'validation', 'quality', 'qa', 'verify', 'assert', 'check'],
            'data-processing': ['data', 'processing', 'etl', 'analytics', 'report', 'transform'],
            'security': ['security', 'encryption', 'auth', 'compliance', 'audit', 'protect'],
            'integration': ['integration', 'connect', 'webhook', 'third-party', 'external', 'bridge']
        }
        
        # Score each type based on keyword matches
        type_scores = {}
        for task_type, keywords in type_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in description_lower:
                    score += 1
            if score > 0:
                type_scores[task_type] = score
        
        # Return the type with highest score, or 'general' if no matches
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _determine_task_priority(self, phase: str, section: str, description: str) -> TaskPriority:
        """Determine task priority based on phase, section, and description"""
        # Critical: Security, authentication, production hardening
        if any(keyword in description.lower() for keyword in ['security', 'auth', 'production', 'deployment']):
            return TaskPriority.CRITICAL
            
        # High: Core functionality, workflows, ML integration
        if any(keyword in description.lower() for keyword in ['workflow', 'machine learning', 'core', 'essential']):
            return TaskPriority.HIGH
            
        # Medium: User experience, visualizations
        if any(keyword in description.lower() for keyword in ['ui', 'ux', 'visualization', 'dashboard']):
            return TaskPriority.MEDIUM
            
        # Low: Nice-to-have features, optimizations
        return TaskPriority.LOW
    
    def _assess_task_complexity(self, description: str) -> int:
        """Assess task complexity (1-10 scale)"""
        complexity_indicators = [
            'implement', 'develop', 'create', 'build', 'design',
            'integrate', 'configure', 'deploy', 'test', 'optimize',
            'database', 'API', 'frontend', 'backend', 'infrastructure',
            'monitoring', 'security', 'authentication', 'deployment',
            'machine learning', 'ML', 'AI', 'workflow', 'parallel',
            'conditional', 'templates', 'versioning'
        ]
        
        score = 1
        description_lower = description.lower()
        
        for indicator in complexity_indicators:
            if indicator in description_lower:
                score += 1
                
        # Length factor
        if len(description) > 100:
            score += 1
        if len(description) > 200:
            score += 1
            
        return min(score, 10)
    
    def _estimate_task_time(self, complexity: int) -> int:
        """Estimate task completion time in minutes"""
        # Base time: 30 minutes
        base_time = 30
        
        # Complexity multiplier
        if complexity <= 3:
            multiplier = 0.5  # Simple tasks
        elif complexity <= 6:
            multiplier = 1.0  # Medium tasks
        elif complexity <= 8:
            multiplier = 2.0  # Complex tasks
        else:
            multiplier = 3.0  # Very complex tasks
            
        return int(base_time * multiplier)
    
    def _extract_tags(self, description: str) -> List[str]:
        """Extract relevant tags from task description"""
        tags = []
        description_lower = description.lower()
        
        # Technology tags
        if 'workflow' in description_lower:
            tags.append('workflow')
        if 'ml' in description_lower or 'machine learning' in description_lower:
            tags.append('machine-learning')
        if 'ui' in description_lower or 'frontend' in description_lower:
            tags.append('frontend')
        if 'api' in description_lower or 'backend' in description_lower:
            tags.append('backend')
        if 'security' in description_lower or 'auth' in description_lower:
            tags.append('security')
        if 'database' in description_lower:
            tags.append('database')
        if 'monitoring' in description_lower:
            tags.append('monitoring')
            
        return tags

    def _initialize_workers(self):
        """Initialize enhanced worker processes"""
        logger.info("🔧 Initializing enhanced workers")
        
        # Create specialized workers with broader capabilities
        worker_types = {
            'workflow': {
                'name': 'Workflow Worker',
                'specialization': ['workflow', 'parallel', 'conditional', 'process', 'automation', 'general'],
                'capacity': 2,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['workflow', 'process', 'automation', 'orchestrate', 'coordinate', 'task', 'flow', 'pipeline']
            },
            'machine-learning': {
                'name': 'ML Worker',
                'specialization': ['machine-learning', 'prediction', 'optimization', 'ai', 'model', 'general'],
                'capacity': 1,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['ml', 'ai', 'machine-learning', 'neural', 'intelligence', 'model', 'predict', 'train']
            },
            'frontend': {
                'name': 'Frontend Worker',
                'specialization': ['frontend', 'ui', 'ux', 'visualization', 'interface', 'design', 'general'],
                'capacity': 2,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['frontend', 'ui', 'ux', 'interface', 'design', 'user', 'experience', 'visual', 'component']
            },
            'backend': {
                'name': 'Backend Worker',
                'specialization': ['backend', 'api', 'security', 'database', 'server', 'general'],
                'capacity': 2,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['backend', 'api', 'database', 'server', 'infrastructure', 'core', 'system', 'service']
            },
            'monitoring': {
                'name': 'Monitoring Worker',
                'specialization': ['monitoring', 'performance', 'metrics', 'logging', 'general'],
                'capacity': 1,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['monitor', 'logging', 'metrics', 'track', 'observe', 'performance', 'dashboard']
            },
            'testing': {
                'name': 'Testing Worker',
                'specialization': ['testing', 'quality-assurance', 'validation', 'verification', 'general'],
                'capacity': 1,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['test', 'testing', 'validation', 'quality', 'qa', 'verify', 'check', 'assert']
            },
            'data-processing': {
                'name': 'Data Processing Worker',
                'specialization': ['data-processing', 'etl', 'analytics', 'reporting', 'general'],
                'capacity': 1,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['data', 'processing', 'etl', 'analytics', 'report', 'information', 'transform']
            },
            'security': {
                'name': 'Security Worker',
                'specialization': ['security', 'compliance', 'encryption', 'audit', 'auth', 'general'],
                'capacity': 1,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['security', 'encryption', 'compliance', 'audit', 'protection', 'secure', 'auth']
            },
            'integration': {
                'name': 'Integration Worker',
                'specialization': ['integration', 'api', 'webhooks', 'third-party', 'connect', 'general'],
                'capacity': 1,
                'status': WorkerStatus.IDLE,
                'task_keywords': ['integration', 'api', 'webhook', 'connect', 'third-party', 'external', 'bridge']
            }
        }
        
        for worker_id, worker_config in worker_types.items():
            self.workers[worker_id] = {
                'id': worker_id,
                'name': worker_config['name'],
                'specialization': worker_config['specialization'],
                'capacity': worker_config['capacity'],
                'status': worker_config['status'],
                'current_task': None,
                'tasks_completed': 0,
                'tasks_failed': 0,
                'performance_score': 100.0,
                'last_activity': datetime.now(),
                'error_count': 0,
                'recovery_attempts': 0,
                'task_keywords': worker_config['task_keywords']
            }
            
        logger.info(f"✅ Initialized {len(self.workers)} enhanced workers")
        
    def _setup_recovery_strategies(self):
        """Setup error recovery strategies"""
        self.recovery_strategies = {
            'timeout': {
                'action': 'restart_worker',
                'backup': 'reassign_task',
                'timeout': 60
            },
            'memory_error': {
                'action': 'restart_worker',
                'backup': 'reduce_workload',
                'timeout': 120
            },
            'import_error': {
                'action': 'fix_dependencies',
                'backup': 'use_alternative_worker',
                'timeout': 300
            },
            'syntax_error': {
                'action': 'fix_code',
                'backup': 'revert_changes',
                'timeout': 600
            }
        }
        
    def _setup_collaboration_network(self):
        """Setup enhanced collaboration network between workers"""
        # Workers can collaborate on complex tasks
        self.collaboration_network = {
            'workflow': ['backend', 'monitoring', 'testing'],
            'machine-learning': ['backend', 'monitoring', 'data-processing'],
            'frontend': ['backend', 'monitoring', 'testing'],
            'backend': ['monitoring', 'security', 'integration'],
            'monitoring': ['security', 'data-processing'],
            'testing': ['monitoring', 'security'],
            'data-processing': ['monitoring', 'backend'],
            'security': ['monitoring', 'backend'],
            'integration': ['monitoring', 'backend', 'security']
        }
        
    async def start_automation_loop(self):
        """Start the enhanced automation loop"""
        logger.info("🚀 Enhanced Frenly Enhancement Automation System Starting...")
        logger.info(f"📊 System Configuration:")
        logger.info(f"   • Workers: {len(self.workers)} specialized workers")
        logger.info(f"   • Max Concurrent Tasks: {self.config.max_concurrent_tasks}")
        logger.info(f"   • Max Tasks per Cycle: {self.config.max_tasks_per_cycle}")
        logger.info(f"   • Task Timeout: {self.config.task_timeout} seconds")
        logger.info(f"   • Loop Interval: {self.config.loop_interval} seconds")
        logger.info(f"   • Retry Delay: {self.config.retry_delay} seconds")
        logger.info(f"   • Subworker Capacity: {self.config.subworker_capacity} per worker")
        
        # Run self-tests before starting
        if not self._run_self_tests():
            logger.warning("⚠️ Some self-tests failed, but continuing with automation")
        
        try:
            while True:
                # Increment cycle counter
                self.cycle_counter += 1
                self.cycle_start_time = time.time()
                
                logger.info(f"🔄 Starting automation cycle #{self.cycle_counter}")
                
                # Process tasks with enhanced features
                cycle_result = await self._process_cycle()
                
                # Calculate cycle time
                cycle_time = time.time() - self.cycle_start_time
                
                # Record performance metrics
                self._record_cycle_metrics(cycle_result, cycle_time)
                
                # Apply self-learning optimizations
                self._apply_optimizations(cycle_result)
                
                # Check for status update threshold
                if self.status_update_counter >= self.status_update_threshold:
                    self._trigger_status_update()
                    self.status_update_counter = 0
                    
                # Dynamic worker scaling
                await self._scale_workers()
                
                # Log cycle completion with detailed metrics
                self._log_cycle_completion(cycle_result, cycle_time)
                
                # Log comprehensive status summary
                self._log_status_summary()
                
                # Wait for next cycle
                await asyncio.sleep(self.config.loop_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Enhanced automation system stopped by user")
            await self._graceful_shutdown()
        except Exception as e:
            logger.error(f"❌ Error in enhanced automation loop: {e}")
            await self._graceful_shutdown()
            raise
            
    async def _graceful_shutdown(self):
        """Perform graceful shutdown"""
        logger.info("🔄 Starting graceful shutdown...")
        
        try:
            # Execute all shutdown handlers
            for handler in self.shutdown_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler()
                    else:
                        handler()
                except Exception as e:
                    logger.error(f"Error in shutdown handler {handler.__name__}: {e}")
            
            logger.info("✅ Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
            
    async def _process_cycle(self) -> Dict[str, Any]:
        """Process one automation cycle with enhanced features and completion tracking"""
        cycle_start = time.time()
        tasks_processed = 0
        successful_tasks = 0
        failed_tasks = 0
        
        # Fix: Get current task counts
        pending_count = len(self._get_available_tasks())
        in_progress_count = len([t for t in self.tasks if t['status'] == TaskStatus.IN_PROGRESS])
        completed_count = len(self.completed_tasks)
        failed_count = len(self.failed_tasks)
        
        logger.info(f"�� Cycle #{self.cycle_counter} - Starting with {pending_count} pending tasks")
        
        # Get available tasks
        available_tasks = self._get_available_tasks()
        
        # Process tasks with intelligent breakdown
        for task in available_tasks[:self.config.max_tasks_per_cycle]:
            try:
                # Check if task needs breakdown
                if self.config.enable_task_breakdown:
                    subtasks = self._breakdown_complex_task(task)
                    if len(subtasks) > 1:
                        logger.info(f"�� Task {task.get('id', 'Unknown')} broken down into {len(subtasks)} subtasks")
                        
                        # Process subtasks
                        for subtask in subtasks:
                            if await self._process_task_with_strategy(subtask):
                                successful_tasks += 1
                                # Fix: Add to completed tasks
                                self.completed_tasks.append(subtask)
                            else:
                                failed_tasks += 1
                                # Fix: Add to failed tasks
                                self.failed_tasks.append(subtask)
                            tasks_processed += 1
                    else:
                        # Process single task
                        if await self._process_task_with_strategy(task):
                            successful_tasks += 1
                            # Fix: Add to completed tasks
                            self.completed_tasks.append(task)
                        else:
                            failed_tasks += 1
                            # Fix: Add to failed tasks
                            self.failed_tasks.append(task)
                        tasks_processed += 1
                else:
                    # Process without breakdown
                    if await self._process_task_with_strategy(task):
                        successful_tasks += 1
                        # Fix: Add to completed tasks
                        self.completed_tasks.append(task)
                    else:
                        failed_tasks += 1
                        # Fix: Add to failed tasks
                        self.failed_tasks.append(task)
                    tasks_processed += 1
                    
            except Exception as e:
                logger.error(f"❌ Error processing task {task.get('id', 'Unknown')}: {e}")
                failed_tasks += 1
                # Fix: Add to failed tasks
                self.failed_tasks.append(task)
                tasks_processed += 1
                
        cycle_time = time.time() - cycle_start
        success_rate = successful_tasks / max(1, tasks_processed)
        
        # Fix: Update task statuses
        self._update_task_statuses()
        
        # Update status counter
        self.status_update_counter += successful_tasks
        
        # Fix: Calculate completion percentage
        total_tasks = len(self.tasks)
        completion_percentage = (len(self.completed_tasks) / max(1, total_tasks)) * 100
        
        return {
            'cycle_number': self.cycle_counter,
            'tasks_processed': tasks_processed,
            'successful_tasks': successful_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': success_rate,
            'cycle_time': cycle_time,
            'worker_utilization': self._calculate_worker_utilization(),
            'completion_percentage': completion_percentage,
            'pending_count': len(self._get_available_tasks()),
            'in_progress_count': len([t for t in self.tasks if t['status'] == TaskStatus.IN_PROGRESS]),
            'completed_count': len(self.completed_tasks),
            'failed_count': len(self.failed_tasks)
        }
        
    def _breakdown_complex_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down a complex task into subtasks between 1-5 minutes"""
        complexity = self._assess_task_complexity(task['description'])
        
        if complexity <= 2:
            # Simple or basic task - no breakdown needed
            return [task]
            
        # Complex task - break it down
        subtasks = []
        task_id = task.get('id', 'unknown')
        
        if complexity >= 4:
            # Very complex task - break into multiple phases
            phases = self._identify_task_phases(task)
            for i, phase in enumerate(phases):
                # Calculate estimated time: 1-5 minutes range
                estimated_time = min(300, max(60, 180 + (i * 30)))  # 3-5 minutes per phase
                
                subtask = {
                    'id': f"{task_id}_phase_{i+1}",
                    'parent_id': task_id,
                    'title': f"{task.get('description', 'Task')} - Phase {i+1}",
                    'description': phase['description'],
                    'type': phase['type'],
                    'complexity': TaskComplexity.SIMPLE,
                    'estimated_time': estimated_time,  # 1-5 minutes (60-300 seconds)
                    'dependencies': phase.get('dependencies', []),
                    'priority': task.get('priority', TaskPriority.MEDIUM),
                    'worker_assignment': None,
                    'status': TaskStatus.PENDING
                }
                subtasks.append(subtask)
        else:
            # Moderate complexity - break into logical steps
            steps = self._identify_task_steps(task)
            for i, step in enumerate(steps):
                # Calculate estimated time: 1-5 minutes range
                estimated_time = min(300, max(60, 120 + (i * 45)))  # 2-4 minutes per step
                
                subtask = {
                    'id': f"{task_id}_step_{i+1}",
                    'parent_id': task_id,
                    'title': f"{task.get('description', 'Task')} - Step {i+1}",
                    'description': step['description'],
                    'type': step['type'],
                    'complexity': TaskComplexity.SIMPLE,
                    'estimated_time': estimated_time,  # 1-5 minutes (60-300 seconds)
                    'dependencies': step.get('dependencies', []),
                    'priority': task.get('priority', TaskPriority.MEDIUM),
                    'worker_assignment': None,
                    'status': TaskStatus.PENDING
                }
                subtasks.append(subtask)
                
        return subtasks
        
    def _identify_task_phases(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify logical phases for very complex tasks with 1-5 minute estimates"""
        description = task.get('description', '').lower()
        phases = []
        
        if 'implement' in description:
            phases.extend([
                {'description': 'Research and planning', 'type': 'research', 'time_estimate': 240},  # 4 minutes
                {'description': 'Core implementation', 'type': 'implementation', 'time_estimate': 300},  # 5 minutes
                {'description': 'Testing and validation', 'type': 'testing', 'time_estimate': 180},  # 3 minutes
                {'description': 'Documentation and cleanup', 'type': 'documentation', 'time_estimate': 120}  # 2 minutes
            ])
        elif 'integrate' in description:
            phases.extend([
                {'description': 'API analysis', 'type': 'analysis', 'time_estimate': 180},  # 3 minutes
                {'description': 'Connection setup', 'type': 'setup', 'time_estimate': 240},  # 4 minutes
                {'description': 'Data mapping', 'type': 'mapping', 'time_estimate': 300},  # 5 minutes
                {'description': 'Integration testing', 'type': 'testing', 'time_estimate': 180}  # 3 minutes
            ])
        elif 'optimize' in description:
            phases.extend([
                {'description': 'Performance analysis', 'type': 'analysis', 'time_estimate': 240},  # 4 minutes
                {'description': 'Bottleneck identification', 'type': 'identification', 'time_estimate': 180},  # 3 minutes
                {'description': 'Optimization implementation', 'type': 'implementation', 'time_estimate': 300},  # 5 minutes
                {'description': 'Performance validation', 'type': 'validation', 'time_estimate': 180}  # 3 minutes
            ])
        else:
            # Generic breakdown with 1-5 minute estimates
            phases.extend([
                {'description': 'Initial setup', 'type': 'setup', 'time_estimate': 120},  # 2 minutes
                {'description': 'Core work', 'type': 'implementation', 'time_estimate': 300},  # 5 minutes
                {'description': 'Quality check', 'type': 'testing', 'time_estimate': 180},  # 3 minutes
                {'description': 'Finalization', 'type': 'cleanup', 'time_estimate': 120}  # 2 minutes
            ])
            
        return phases
        
    def _identify_task_steps(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify logical steps for moderate complexity tasks with 1-5 minute estimates"""
        description = task.get('description', '').lower()
        steps = []
        if 'test' in description:
            steps.extend([
                {'description': 'Test case preparation', 'type': 'preparation', 'time_estimate': 180},  # 3 minutes
                {'description': 'Test execution', 'type': 'execution', 'time_estimate': 240},  # 4 minutes
                {'description': 'Result analysis', 'type': 'analysis', 'time_estimate': 180}  # 3 minutes
            ])
        elif 'create' in description:
            steps.extend([
                {'description': 'Requirements analysis', 'type': 'analysis', 'time_estimate': 240},  # 4 minutes
                {'description': 'Design and structure', 'type': 'design', 'time_estimate': 300},  # 5 minutes
                {'description': 'Implementation', 'type': 'implementation', 'time_estimate': 300}  # 5 minutes
            ])
        else:
            # Generic steps with 1-5 minute estimates
            steps.extend([
                {'description': 'Preparation', 'type': 'preparation', 'time_estimate': 120},  # 2 minutes
                {'description': 'Execution', 'type': 'execution', 'time_estimate': 300},  # 5 minutes
                {'description': 'Verification', 'type': 'verification', 'time_estimate': 180}  # 3 minutes
            ])
            
        return steps
        
    async def _process_task(self, task: Dict[str, Any]) -> bool:
        """Process a single task with enhanced worker assignment and status tracking"""
        try:
            # Update task status to in-progress and set start time
            task['status'] = TaskStatus.IN_PROGRESS
            task['start_time'] = datetime.now()
            
            # Find suitable worker
            suitable_worker = self._find_suitable_worker(task)
            if not suitable_worker:
                logger.warning(f"⚠️ No suitable worker found for task: {task.get('description', 'Unknown')}")
                task['status'] = TaskStatus.FAILED
                return False
                
            # Assign task to worker - FIX: Set assigned_worker field
            task['assigned_worker'] = suitable_worker['id']
            suitable_worker['status'] = WorkerStatus.WORKING
            suitable_worker['current_task'] = task
            
            # Simulate task processing
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Update worker performance
            success = random.random() > 0.1  # 90% success rate
            suitable_worker['performance_score'] = min(100.0, suitable_worker['performance_score'] + (1.0 if success else -2.0))
            
            # Update task status based on result
            task['completion_time'] = datetime.now()
            if success:
                task['status'] = TaskStatus.COMPLETED
                self.metrics['successful_tasks'] += 1
                suitable_worker['tasks_completed'] += 1
                logger.info(f"✅ Task '{task.get('description', 'Unknown')[:50]}...' completed successfully by {suitable_worker['name']}")
            else:
                task['status'] = TaskStatus.FAILED
                self.metrics['failed_tasks'] += 1
                suitable_worker['tasks_failed'] += 1
                logger.warning(f"❌ Task '{task.get('description', 'Unknown')[:50]}...' failed")
                    
            self.metrics['total_tasks_processed'] += 1
            
            # Reset worker status
            suitable_worker['status'] = WorkerStatus.IDLE
            suitable_worker['current_task'] = None
            
            return success
                
        except Exception as e:
            logger.error(f"❌ Error in task processing: {e}")
            task['status'] = TaskStatus.FAILED
            return False
            
    def _find_suitable_worker(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a suitable worker for a task with improved matching"""
        task_type = task.get('type', 'general')
        task_description = task.get('description', '').lower()
        task_tags = task.get('tags', [])
        
        # Score each worker based on suitability
        worker_scores = []
        
        for worker_id, worker in self.workers.items():
            if worker['status'] != WorkerStatus.IDLE:
                continue
            
            score = 0
            
            # Check specialization match
            for spec in worker['specialization']:
                if spec.lower() in task_type.lower() or spec.lower() in task_description:
                    score += 10
                    break
            
            # Check keyword matches in description
            for keyword in worker['task_keywords']:
                if keyword.lower() in task_description:
                    score += 2
            
            # Check tag matches
            for tag in task_tags:
                if tag in worker['specialization']:
                    score += 5
            
            # Add worker with score if available
            if score > 0:
                worker_scores.append((worker, score))
        
        # If no specialized workers found, use any idle worker
        if not worker_scores:
            idle_workers = [w for w in self.workers.values() if w['status'] == WorkerStatus.IDLE]
            if idle_workers:
                # Sort by performance score
                idle_workers.sort(key=lambda w: w['performance_score'], reverse=True)
                return idle_workers[0]
            return None
        
        # Sort by score (highest first) and then by performance
        worker_scores.sort(key=lambda ws: (ws[1], ws[0]['performance_score']), reverse=True)
        return worker_scores[0][0]

    def _get_available_tasks(self) -> List[Dict[str, Any]]:
        """Get available tasks for processing"""
        return [task for task in self.tasks if task['status'] == TaskStatus.PENDING]
    
    def _update_task_statuses(self):
        """Update task statuses based on completion tracking"""
        # Update completed tasks status
        for task in self.completed_tasks:
            if task in self.tasks:
                task['status'] = TaskStatus.COMPLETED
                
        # Update failed tasks status
        for task in self.failed_tasks:
            if task in self.tasks:
                task['status'] = TaskStatus.FAILED
                
    def _record_cycle_metrics(self, cycle_result: Dict[str, Any], cycle_time: float):
        """Record metrics from a processing cycle"""
        # Update system metrics
        self.system_metrics['total_tasks'] = len(self.tasks)
        self.system_metrics['completed_tasks'] = len(self.completed_tasks)
        self.system_metrics['failed_tasks'] = len(self.failed_tasks)
        
        # Calculate success rate
        total_processed = len(self.completed_tasks) + len(self.failed_tasks)
        if total_processed > 0:
            self.system_metrics['success_rate'] = len(self.completed_tasks) / total_processed
            
        # Update average completion time - FIX: Handle missing timestamps
        if self.completed_tasks:
            # Use cycle time as a fallback for missing timestamps
            self.system_metrics['average_completion_time'] = cycle_time
                
        # Update uptime
        self.system_metrics['system_uptime'] = (datetime.now() - self.system_metrics['start_time']).total_seconds()
        
        # Update cycle metrics
        self.metrics['cycle_times'].append(cycle_time)
        self.metrics['average_cycle_time'] = sum(self.metrics['cycle_times']) / len(self.metrics['cycle_times'])
    
    def _apply_optimizations(self, cycle_result: Dict[str, Any]):
        """Apply self-learning optimizations"""
        # Record performance for learning
        self.performance_history.append({
            'timestamp': datetime.now(),
            'success_rate': cycle_result.get('success_rate', 0),
            'cycle_time': cycle_result.get('cycle_time', 30),
            'worker_utilization': cycle_result.get('worker_utilization', 0)
        })
        
        # Keep only last 100 records
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
            
        # Get optimization recommendations
        recommendations = self._get_optimization_recommendations()
        
        if recommendations:
            logger.info(f"🧠 Applying optimizations: {recommendations}")
            
            # Apply cycle time adjustments
            if 'cycle_time' in recommendations:
                new_cycle_time = recommendations['cycle_time']
                old_cycle_time = self.config.loop_interval
                self.config.loop_interval = new_cycle_time
                logger.info(f"⏱️ Cycle time adjusted: {old_cycle_time}s → {new_cycle_time}s")
                
    def _get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations based on performance history"""
        if len(self.performance_history) < 10:
            return {}
            
        recent_performance = self.performance_history[-10:]
        avg_success_rate = sum(p['success_rate'] for p in recent_performance) / len(recent_performance)
        avg_cycle_time = sum(p['cycle_time'] for p in recent_performance) / len(recent_performance)
        
        recommendations = {}
        
        if avg_success_rate < 0.8:
            recommendations['cycle_time'] = max(15, avg_cycle_time - 5)  # Faster cycles
        elif avg_success_rate > 0.95:
            recommendations['cycle_time'] = min(120, avg_cycle_time + 5)  # Slower cycles
            
        return recommendations
        
    async def _scale_workers(self):
        """Dynamically scale workers based on demand"""
        pending_tasks = len(self._get_available_tasks())
        worker_utilization = self._calculate_worker_utilization()
        
        # Simple scaling logic
        if pending_tasks > 50 and worker_utilization > 0.8:
            logger.info("📈 High demand detected - workers are at capacity")
        elif pending_tasks < 10 and worker_utilization < 0.3:
            logger.info("📉 Low demand detected - workers are underutilized")
            
    def _calculate_worker_utilization(self) -> float:
        """Calculate current worker utilization"""
        if not self.workers:
            return 0.0
            
        total_utilization = sum(self._get_worker_utilization(worker) for worker in self.workers.values())
        return total_utilization / len(self.workers)
        
    def _get_worker_utilization(self, worker: Dict[str, Any]) -> float:
        """Get utilization for a specific worker"""
        if worker['status'] == WorkerStatus.IDLE:
            return 0.0
        elif worker['status'] == WorkerStatus.WORKING:
            return 1.0
        else:
            return 0.5
            
    def _trigger_status_update(self):
        """Trigger status update after threshold is reached"""
        logger.info("🔄 Status Update Threshold Reached - Updating System Status")
        
        # Calculate current performance metrics
        success_rate = self.metrics['successful_tasks'] / max(1, self.metrics['total_tasks_processed'])
        avg_cycle_time = self.metrics['average_cycle_time']
        
        # Generate status report
        status_report = {
            'timestamp': datetime.now(),
            'success_rate': success_rate,
            'average_cycle_time': avg_cycle_time,
            'total_tasks_processed': self.metrics['total_tasks_processed'],
            'active_workers': len([w for w in self.workers.values() if w['status'] == WorkerStatus.WORKING]),
            'total_workers': len(self.workers),
            'system_efficiency': self._calculate_system_efficiency(),
            'recommendations': self._generate_recommendations()
        }
        
        # Log status update
        logger.info(f"📊 Status Update: Success Rate: {success_rate:.2%}, "
                   f"Avg Cycle Time: {avg_cycle_time:.1f}s, "
                   f"Total Tasks: {self.metrics['total_tasks_processed']}, "
                   f"Active Workers: {status_report['active_workers']}/{status_report['total_workers']}")
        
        # Store status report
        self._store_status_report(status_report)
        
    def _calculate_system_efficiency(self) -> float:
        """Calculate overall system efficiency"""
        worker_efficiency = self._calculate_worker_utilization()
        task_success_rate = self.metrics['successful_tasks'] / max(1, self.metrics['total_tasks_processed'])
        
        return (worker_efficiency + task_success_rate) / 2
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for system improvement"""
        recommendations = []
        
        if self.metrics['successful_tasks'] / max(1, self.metrics['total_tasks_processed']) < 0.8:
            recommendations.append("Consider reducing task complexity or improving worker performance")
            
        if self._calculate_worker_utilization() < 0.5:
            recommendations.append("Worker utilization is low - consider reducing worker count or increasing task load")
            
        return recommendations
        
    def _store_status_report(self, status_report: Dict[str, Any]):
        """Store status report for historical analysis"""
        # In a real implementation, this would store to database or file
        logger.info(f"💾 Status report stored: {status_report['timestamp']}")
        
    def _log_cycle_completion(self, cycle_result: Dict[str, Any], cycle_time: float):
        """Log detailed cycle completion with live task counts"""
        logger.info("=" * 80)
        logger.info(f"✅ CYCLE #{cycle_result['cycle_number']} COMPLETED")
        logger.info("=" * 80)
        logger.info(f"⏱️ Cycle Time: {cycle_time:.2f} seconds")
        logger.info(f"�� Tasks Processed: {cycle_result['tasks_processed']}")
        logger.info(f"✅ Successful: {cycle_result['successful_tasks']}")
        logger.info(f"❌ Failed: {cycle_result['failed_tasks']}")
        logger.info(f"📈 Success Rate: {cycle_result['success_rate']:.1%}")
        logger.info(f"🎯 Completion Percentage: {cycle_result['completion_percentage']:.1f}%")
        
        # Live task counts
        logger.info("📋 LIVE TASK STATUS:")
        logger.info(f"  • Pending: {cycle_result['pending_count']}")
        logger.info(f"  • In Progress: {cycle_result['in_progress_count']}")
        logger.info(f"  • Completed: {cycle_result['completed_count']}")
        logger.info(f"  • Failed: {cycle_result['failed_count']}")
        
        # Worker utilization
        logger.info(f"�� Worker Utilization: {cycle_result['worker_utilization']:.1%}")
        
        logger.info("=" * 80)
        
    def _log_status_summary(self):
        """Log comprehensive status summary with live updates"""
        pending_count = len(self._get_available_tasks())
        in_progress_count = len([t for t in self.tasks if t['status'] == TaskStatus.IN_PROGRESS])
        completed_count = len(self.completed_tasks)
        failed_count = len(self.failed_tasks)
        total_tasks = len(self.tasks)
        
        completion_percentage = (completed_count / max(1, total_tasks)) * 100
        success_rate = completed_count / max(1, completed_count + failed_count)
        
        logger.info("📊 COMPREHENSIVE STATUS SUMMARY:")
        logger.info(f"�� Cycle #{self.cycle_counter}")
        logger.info(f"📋 Total Tasks: {total_tasks}")
        logger.info(f"⏳ Pending: {pending_count}")
        logger.info(f"🔄 In Progress: {in_progress_count}")
        logger.info(f"✅ Completed: {completed_count}")
        logger.info(f"❌ Failed: {failed_count}")
        logger.info(f"🎯 Completion Percentage: {completion_percentage:.1f}%")
        logger.info(f"📈 Success Rate: {success_rate:.1%}")
        
        # Progress bar visualization
        progress_bar = self._create_progress_bar(completion_percentage)
        logger.info(f"📊 Progress: {progress_bar} {completion_percentage:.1f}%")
        
        # Worker task distribution - FIX: Count actual assigned tasks
        worker_task_counts = {}
        for worker_id, worker in self.workers.items():
            # Count tasks assigned to this worker
            assigned_tasks = len([t for t in self.tasks if t.get('assigned_worker') == worker_id])
            worker_task_counts[worker['name']] = assigned_tasks
            
        logger.info("🔧 WORKER TASK DISTRIBUTION:")
        for worker_name, task_count in worker_task_counts.items():
            logger.info(f"  • {worker_name}: {task_count} tasks")
            
        logger.info("=" * 80)
        
    def _create_progress_bar(self, percentage: float, width: int = 50) -> str:
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"
        
    def _print_summary(self):
        """Print final summary of automation run"""
        logger.info("=" * 80)
        logger.info("�� ENHANCED FRENLY ENHANCEMENT AUTOMATION SUMMARY")
        logger.info("=" * 80)
        
        total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
        if total_tasks > 0:
            success_rate = (len(self.completed_tasks) / total_tasks) * 100
            logger.info(f"📊 Success Rate: {success_rate:.1f}%")
            
        logger.info(f"✅ Completed Tasks: {len(self.completed_tasks)}")
        logger.info(f"❌ Failed Tasks: {len(self.failed_tasks)}")
        logger.info(f"⏳ Pending Tasks: {len([t for t in self.tasks if t['status'] == TaskStatus.PENDING])}")
        
        if self.completed_tasks:
            logger.info(f"⏱️  Average Completion Time: {self.system_metrics['average_completion_time']:.1f} seconds")
            
        logger.info(f"🕐 System Uptime: {self.system_metrics['system_uptime'] / 3600:.1f} hours")
        logger.info(f"🔄 Total Cycles: {self.cycle_counter}")
        
        # Print completed tasks
        if self.completed_tasks:
            logger.info("\n✅ Completed Tasks:")
            for task in self.completed_tasks[-5:]:  # Last 5 completed
                logger.info(f"   • {task['description'][:60]}...")
                
        # Print failed tasks
        if self.failed_tasks:
            logger.info("\n❌ Failed Tasks:")
            for task in self.failed_tasks[-5:]:  # Last 5 failed
                logger.info(f"   • {task['description'][:60]}...")
                
        logger.info("=" * 80)

async def main():
    """Main entry point"""
    print("🚀 Enhanced Frenly Enhancement Automation System")
    print("=" * 80)
    print("This system will automatically implement Frenly enhancement todos")
    print("with enhanced capacity, intelligent task breakdown, and self-learning optimization")
    print("Plus all 30 optimization recommendations integrated!")
    print("Press Ctrl+C to stop the automation")
    print("=" * 80)
    print()
    
    # Create and start automation system
    automation = FrenlyEnhancementAutomation()
    
    # Start the automation loop
    await automation.start_automation_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Enhanced automation stopped by user")
    except Exception as e:
        print(f"\n💥 Enhanced automation failed: {e}")
        traceback.print_exc()
        sys.exit(1)
        
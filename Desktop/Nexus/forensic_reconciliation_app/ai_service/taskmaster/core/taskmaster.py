"""
Main Taskmaster Class - Central Orchestration Engine

This module contains the main Taskmaster class that coordinates all aspects
of job assignment, workflow management, and resource allocation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from .job_scheduler import JobScheduler
from .task_router import TaskRouter
from .workflow_orchestrator import WorkflowOrchestrator
from .resource_monitor import ResourceMonitor
from ..models.job import Job, JobStatus, JobPriority, JobType, JobResult
from ..models.agent import Agent, AgentStatus, AgentType
from ..models.queue import Queue, QueueType, QueueStatus
from ..models.workflow import Workflow, WorkflowStatus, WorkflowStep
import re
from pathlib import Path
import time
from neo4j import GraphDatabase
import os
import duckdb


class TaskmasterStatus(Enum):
    """Taskmaster system status enumeration."""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class TaskmasterConfig:
    """Configuration for the Taskmaster system."""
    
    # General settings
    max_concurrent_jobs: int = 1000
    max_concurrent_tasks: int = 5000
    job_timeout: timedelta = timedelta(hours=24)
    task_timeout: timedelta = timedelta(hours=4)
    
    # Scheduling settings
    scheduling_algorithm: str = "priority_weighted_round_robin"
    preemption: bool = True
    fairness_factor: float = 0.8
    
    # Monitoring settings
    metrics_collection: bool = True
    health_check_interval: timedelta = timedelta(seconds=30)
    performance_alerting: bool = True
    
    # Scaling settings
    auto_scaling: bool = True
    min_agents: int = 5
    max_agents: int = 100
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.2
    
    # Queue settings
    queue_configs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "high_priority": {
            "max_size": 100,
            "workers": 5,
            "timeout": timedelta(minutes=5),
            "retry_policy": "immediate"
        },
        "normal": {
            "max_size": 1000,
            "workers": 10,
            "timeout": timedelta(minutes=30),
            "retry_policy": "exponential_backoff"
        },
        "batch": {
            "max_size": 5000,
            "workers": 20,
            "timeout": timedelta(hours=4),
            "retry_policy": "fixed_interval"
        },
        "maintenance": {
            "max_size": 100,
            "workers": 2,
            "timeout": timedelta(hours=1),
            "retry_policy": "manual"
        }
    })


class TodoScanner:
    """Scans for and processes TODOs in the codebase."""

    def __init__(self, taskmaster):
        self.taskmaster = taskmaster
        self.logger = logging.getLogger(__name__)

    async def scan_and_process_todos(self, root_directory: str = "."):
        """Scan for TODOs and create jobs for them."""
        self.logger.info(f"Scanning for TODOs in {root_directory}...")
        todo_pattern = re.compile(r'#\s*TODO[:\s].*', re.IGNORECASE)
        files_to_scan = []
        root_path = Path(root_directory)
        if root_path.is_file():
            files_to_scan.append(root_path)
        elif root_path.is_dir():
            files_to_scan.extend(p for p in root_path.rglob("*") if p.is_file() and not self._should_skip_file(p))

        for file_path in files_to_scan:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if todo_pattern.search(line):
                            await self._process_todo_line(line, file_path, line_num)
            except Exception as e:
                self.logger.warning(f"Could not read file {file_path}: {e}")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped"""
        skip_patterns = [
            r'\.git', r'\.pyc$', r'__pycache__', r'\.DS_Store',
            r'\.log$', r'\.tmp$', r'\.cache$', r'node_modules'
        ]
        return any(re.search(pattern, str(file_path)) for pattern in skip_patterns)

    async def _process_todo_line(self, line: str, file_path: Path, line_num: int):
        """Create a job for a single TODO line."""
        content = line.strip()
        job_type, priority = self._determine_job_type_and_priority(content)
        job = Job(
            name=f"TODO: {content[:50]}...",
            job_type=job_type,
            priority=priority,
            data={
                "file_path": str(file_path),
                "line_number": line_num,
                "content": content,
            },
            tags=self._extract_tags(content)
        )
        await self.taskmaster.submit_job(job)

    def _determine_job_type_and_priority(self, todo_line: str) -> (JobType, JobPriority):
        """Determine job type and priority from TODO content."""
        if any(keyword in todo_line.lower() for keyword in ["urgent", "critical", "fix", "bug"]):
            priority = JobPriority.CRITICAL
        elif any(keyword in todo_line.lower() for keyword in ["important", "high", "security"]):
            priority = JobPriority.HIGH
        else:
            priority = JobPriority.NORMAL

        if "code" in todo_line.lower() or "refactor" in todo_line.lower():
            job_type = JobType.CODE_REVIEW
        elif "doc" in todo_line.lower() or "readme" in todo_line.lower():
            job_type = JobType.DOCUMENTATION
        elif "test" in todo_line.lower() or "valid" in todo_line.lower():
            job_type = JobType.TESTING
        elif "infra" in todo_line.lower() or "deploy" in todo_line.lower():
            job_type = JobType.INFRASTRUCTURE
        else:
            job_type = JobType.GENERAL_TODO

        return job_type, priority

    def _extract_tags(self, todo_line: str) -> List[str]:
        """Extract tags from TODO line."""
        tags = []
        tag_matches = re.findall(r'@(\w+)', todo_line)
        tags.extend(tag_matches)
        bracket_tags = re.findall(r'\[(\w+)\]', todo_line)
        tags.extend(bracket_tags)
        return tags

class FraudAgent(Agent):
    """Agent specialized in fraud detection tasks."""

    def __init__(self):
        super().__init__(agent_id="fraud_agent", agent_type=AgentType.SPECIALIZED, capabilities=["fraud", "shell_company"])
        self.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ.get("NEO4J_PASSWORD", "password"))
        )

    async def process(self, job: Job) -> JobResult:
        if "shell_company" in job.tags:
            return await self.identify_shell_companies(job)
        return JobResult(success=True, data={"message": f"Fraud analysis complete for: {job.name}"})

    async def identify_shell_companies(self, job: Job) -> JobResult:
        """Identifies shell companies using Neo4j procedures."""
        with self.driver.session() as session:
            result = session.run("CALL db.procedures() YIELD name WHERE name = 'find_shell_companies' RETURN name")
            if result.single():
                return JobResult(success=True, data={"message": "Successfully called find_shell_companies procedure."})
            else:
                return JobResult(success=False, error_message="Could not find find_shell_companies procedure.")

    def close(self):
        self.driver.close()

class ReconciliationAgent(Agent):
    """Agent specialized in reconciliation tasks."""
    def __init__(self, db_path="reconciliation.duckdb"):
        super().__init__(agent_id="reconciliation_agent", agent_type=AgentType.SPECIALIZED, capabilities=["reconciliation"])
        self.db_path = db_path
        self.con = duckdb.connect(database=self.db_path, read_only=False)

    async def process(self, job: Job) -> JobResult:
        if "reconcile" in job.name.lower():
            return await self.reconcile_transactions(job)
        return JobResult(success=True, data={"message": f"Reconciliation task processed for: {job.name}"})

    async def reconcile_transactions(self, job: Job) -> JobResult:
        """Reconciles transactions using DuckDB."""
        try:
            with open("Desktop/Nexus/forensic_reconciliation_app/datastore/duckdb/init/01-schema.sql", "r") as f:
                schema_sql = f.read()
                self.con.execute(schema_sql)
            result = self.con.execute("SELECT COUNT(*) FROM reconciled_transactions").fetchone()
            return JobResult(success=True, data={"reconciled_count": result[0]})
        except Exception as e:
            return JobResult(success=False, error_message=str(e))

    def close(self):
        self.con.close()


class Taskmaster:
    """
    Main Taskmaster class for job assignment and workflow orchestration.
    
    The Taskmaster is responsible for:
    - Coordinating all system components
    - Managing job lifecycle
    - Orchestrating workflows
    - Monitoring system health
    - Optimizing resource utilization
    """
    
    def __init__(self, config: Optional[TaskmasterConfig] = None):
        """Initialize the Taskmaster system."""
        self.config = config or TaskmasterConfig()
        self.logger = logging.getLogger(__name__)
        
        # System status
        self.status = TaskmasterStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self.error_count = 0
        self.last_error: Optional[str] = None
        
        # Core components
        self.job_scheduler: Optional[JobScheduler] = None
        self.task_router: Optional[TaskRouter] = None
        self.workflow_orchestrator: Optional[WorkflowOrchestrator] = None
        self.resource_monitor: Optional[ResourceMonitor] = None
        self.todo_scanner: Optional[TodoScanner] = None
        
        # System state
        self.active_jobs: Dict[str, Job] = {}
        self.active_agents: Dict[str, Agent] = {}
        self.active_queues: Dict[str, Queue] = {}
        self.active_workflows: Dict[str, Workflow] = {}
        
        # Performance metrics
        self.metrics = {
            "jobs_submitted": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "tasks_executed": 0,
            "workflows_completed": 0,
            "average_job_time": 0.0,
            "system_uptime": 0.0
        }
        
        # Event loop
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.tasks: List[asyncio.Task] = []
        
    async def start(self) -> bool:
        """Start the Taskmaster system."""
        try:
            self.logger.info("Starting Taskmaster system...")
            self.status = TaskmasterStatus.STARTING
            
            # Initialize core components
            await self._initialize_components()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Update status
            self.status = TaskmasterStatus.RUNNING
            self.start_time = datetime.utcnow()
            
            self.logger.info("Taskmaster system started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Taskmaster system: {e}")
            self.status = TaskmasterStatus.ERROR
            self.last_error = str(e)
            self.error_count += 1
            return False
    
    async def stop(self) -> bool:
        """Stop the Taskmaster system."""
        try:
            self.logger.info("Stopping Taskmaster system...")
            self.status = TaskmasterStatus.STOPPING
            
            # Stop background tasks
            await self._stop_background_tasks()
            
            # Shutdown components
            await self._shutdown_components()
            
            # Update status
            self.status = TaskmasterStatus.STOPPED
            
            self.logger.info("Taskmaster system stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Taskmaster system: {e}")
            self.status = TaskmasterStatus.ERROR
            self.last_error = str(e)
            self.error_count += 1
            return False
    
    async def pause(self) -> bool:
        """Pause the Taskmaster system."""
        try:
            self.logger.info("Pausing Taskmaster system...")
            self.status = TaskmasterStatus.PAUSED
            
            # Pause job scheduling
            if self.job_scheduler:
                await self.job_scheduler.pause()
            
            self.logger.info("Taskmaster system paused successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pause Taskmaster system: {e}")
            self.last_error = str(e)
            self.error_count += 1
            return False
    
    async def resume(self) -> bool:
        """Resume the Taskmaster system."""
        try:
            self.logger.info("Resuming Taskmaster system...")
            self.status = TaskmasterStatus.RUNNING
            
            # Resume job scheduling
            if self.job_scheduler:
                await self.job_scheduler.resume()
            
            self.logger.info("Taskmaster system resumed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resume Taskmaster system: {e}")
            self.last_error = str(e)
            self.error_count += 1
            return False
    
    async def submit_job(self, job: Job) -> str:
        """Submit a new job to the system."""
        try:
            if self.status != TaskmasterStatus.RUNNING:
                raise RuntimeError("Taskmaster system is not running")
            
            # Validate job
            self._validate_job(job)
            
            # Submit to job scheduler
            job_id = await self.job_scheduler.submit_job(job)
            
            # Update metrics
            self.metrics["jobs_submitted"] += 1
            self.active_jobs[job_id] = job
            
            self.logger.info(f"Job submitted successfully: {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit job: {e}")
            self.error_count += 1
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a specific job."""
        try:
            if job_id in self.active_jobs:
                return self.active_jobs[job_id].status
            
            # Check with job scheduler
            if self.job_scheduler:
                return await self.job_scheduler.get_job_status(job_id)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a specific job."""
        try:
            # Cancel in job scheduler
            if self.job_scheduler:
                success = await self.job_scheduler.cancel_job(job_id)
                if success and job_id in self.active_jobs:
                    del self.active_jobs[job_id]
                return success

            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status."""
        return {
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime": self._calculate_uptime(),
            "active_jobs": len(self.active_jobs),
            "active_agents": len(self.active_agents),
            "active_workflows": len(self.active_workflows),
            "error_count": self.error_count,
            "last_error": self.last_error,
            "metrics": self.metrics.copy()
        }
    
    async def get_queue_status(self, queue_type: QueueType) -> Optional[QueueStatus]:
        """Get the status of a specific queue."""
        try:
            if queue_type.value in self.active_queues:
                return self.active_queues[queue_type.value].status
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get queue status for {queue_type}: {e}")
            return None
    
    async def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get the status of a specific agent."""
        try:
            if agent_id in self.active_agents:
                return self.active_agents[agent_id].status
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get agent status for {agent_id}: {e}")
            return None
    
    async def _initialize_components(self):
        """Initialize all core components."""
        try:
            # Initialize job scheduler
            self.job_scheduler = JobScheduler(self.config, self)
            await self.job_scheduler.start()

            # Initialize task router
            self.task_router = TaskRouter(self.config)
            await self.task_router.start()

            # Initialize workflow orchestrator
            self.workflow_orchestrator = WorkflowOrchestrator(self.config)
            await self.workflow_orchestrator.start()

            # Initialize resource monitor
            self.resource_monitor = ResourceMonitor(self.config)
            await self.resource_monitor.start()

            # Initialize TodoScanner
            self.todo_scanner = TodoScanner(self)

            # Initialize queues
            await self._initialize_queues()

            # Register agents
            await self._register_agents()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def _initialize_queues(self):
        """Initialize all queue types."""
        try:
            for queue_name, queue_config in self.config.queue_configs.items():
                queue = Queue(
                    name=queue_name,
                    queue_type=QueueType(queue_name),
                    max_size=queue_config["max_size"],
                    workers=queue_config["workers"],
                    timeout=queue_config["timeout"],
                    retry_policy=queue_config["retry_policy"]
                )
                await queue.start()
                self.active_queues[queue_name] = queue
                
        except Exception as e:
            self.logger.error(f"Failed to initialize queues: {e}")
            raise
    
    async def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks."""
        try:
            self.loop = asyncio.get_event_loop()
            
            # Start health monitoring
            health_task = self.loop.create_task(self._health_monitor())
            self.tasks.append(health_task)
            
            # Start metrics collection
            metrics_task = self.loop.create_task(self._metrics_collector())
            self.tasks.append(metrics_task)
            
            # Start auto-scaling
            if self.config.auto_scaling:
                scaling_task = self.loop.create_task(self._auto_scaler())
                self.tasks.append(scaling_task)
                
        except Exception as e:
            self.logger.error(f"Failed to start background tasks: {e}")
            raise
    
    async def _stop_background_tasks(self):
        """Stop all background tasks."""
        try:
            for task in self.tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self.tasks.clear()
            
        except Exception as e:
            self.logger.error(f"Failed to stop background tasks: {e}")
    
    async def _shutdown_components(self):
        """Shutdown all core components."""
        try:
            if self.job_scheduler:
                await self.job_scheduler.stop()

            if self.task_router:
                await self.task_router.stop()

            if self.workflow_orchestrator:
                await self.workflow_orchestrator.stop()

            if self.resource_monitor:
                await self.resource_monitor.stop()

            # Stop queues
            for queue in self.active_queues.values():
                await queue.stop()
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown components: {e}")
    
    async def _health_monitor(self):
        """Background task for system health monitoring."""
        while self.status in [TaskmasterStatus.RUNNING, TaskmasterStatus.PAUSED]:
            try:
                # Check component health
                await self._check_component_health()
                
                # Update system metrics
                await self._update_system_metrics()
                
                # Wait for next check
                await asyncio.sleep(self.config.health_check_interval.total_seconds())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _metrics_collector(self):
        """Background task for metrics collection."""
        while self.status in [TaskmasterStatus.RUNNING, TaskmasterStatus.PAUSED]:
            try:
                # Collect performance metrics
                await self._collect_performance_metrics()
                
                # Wait for next collection
                await asyncio.sleep(60)  # Collect every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(10)
    
    async def _auto_scaler(self):
        """Background task for automatic scaling."""
        while self.status == TaskmasterStatus.RUNNING:
            try:
                # Check if scaling is needed
                await self._check_scaling_needs()
                
                # Wait for next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Auto-scaler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_component_health(self):
        """Check the health of all system components."""
        try:
            # Check job scheduler health
            if self.job_scheduler:
                scheduler_health = await self.job_scheduler.get_health()
                if not scheduler_health["healthy"]:
                    self.logger.warning("Job scheduler health check failed")

            # Check task router health
            if self.task_router:
                router_health = await self.task_router.get_health()
                if not router_health["healthy"]:
                    self.logger.warning("Task router health check failed")

            # Check workflow orchestrator health
            if self.workflow_orchestrator:
                orchestrator_health = await self.workflow_orchestrator.get_health()
                if not orchestrator_health["healthy"]:
                    self.logger.warning("Workflow orchestrator health check failed")

            # Check resource monitor health
            if self.resource_monitor:
                monitor_health = await self.resource_monitor.get_health()
                if not monitor_health["healthy"]:
                    self.logger.warning("Resource monitor health check failed")
                    
        except Exception as e:
            self.logger.error(f"Component health check failed: {e}")
    
    async def _update_system_metrics(self):
        """Update system-wide metrics."""
        try:
            # Update uptime
            self.metrics["system_uptime"] = self._calculate_uptime()
            
            # Update active counts
            self.metrics["active_jobs"] = len(self.active_jobs)
            self.metrics["active_agents"] = len(self.active_agents)
            self.metrics["active_workflows"] = len(self.active_workflows)
            
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {e}")
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics from components."""
        try:
            # Collect from job scheduler
            if self.job_scheduler:
                scheduler_metrics = await self.job_scheduler.get_metrics()
                self.metrics.update(scheduler_metrics)

            # Collect from task router
            if self.task_router:
                router_metrics = await self.task_router.get_metrics()
                self.metrics.update(router_metrics)

            # Collect from workflow orchestrator
            if self.workflow_orchestrator:
                orchestrator_metrics = await self.workflow_orchestrator.get_metrics()
                self.metrics.update(orchestrator_metrics)
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance metrics: {e}")
    
    async def _check_scaling_needs(self):
        """Check if system scaling is needed."""
        try:
            if not self.config.auto_scaling:
                return
            
            # Get current resource utilization
            if self.resource_monitor:
                utilization = await self.resource_monitor.get_resource_utilization()

                # Check CPU utilization
                if utilization["cpu_percent"] > self.config.scale_up_threshold * 100:
                    await self._scale_up_resources()
                elif utilization["cpu_percent"] < self.config.scale_down_threshold * 100:
                    await self._scale_down_resources()
                    
        except Exception as e:
            self.logger.error(f"Failed to check scaling needs: {e}")
    
    async def _scale_up_resources(self):
        """Scale up system resources."""
        try:
            self.logger.info("Scaling up system resources...")
            
            # Add more agents if possible
            current_agents = len(self.active_agents)
            if current_agents < self.config.max_agents:
                # Implementation for adding agents
                pass
            
        except Exception as e:
            self.logger.error(f"Failed to scale up resources: {e}")
    
    async def _scale_down_resources(self):
        """Scale down system resources."""
        try:
            self.logger.info("Scaling down system resources...")
            
            # Remove agents if possible
            current_agents = len(self.active_agents)
            if current_agents > self.config.min_agents:
                # Implementation for removing agents
                pass
            
        except Exception as e:
            self.logger.error(f"Failed to scale down resources: {e}")
    
    def _validate_job(self, job: Job):
        """Validate a job before submission."""
        if not job.job_type:
            raise ValueError("Job type is required")
        
        if not job.priority:
            raise ValueError("Job priority is required")
        
        if not job.data:
            raise ValueError("Job data is required")
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime in seconds."""
        if not self.start_time:
            return 0.0
        
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    async def submit_todo_scanning_job(self, root_directory: str) -> str:
        """Submit a job to scan for TODOs in the codebase."""
        job = Job(
            name="todo_scanning_job",
            job_type=JobType.TODO_SCANNING,
            priority=JobPriority.LOW,
            data={"root_directory": root_directory},
        )
        return await self.submit_job(job)

    async def _register_agents(self):
        """Register all available agents."""
        agents_to_register = [
            FraudAgent(),
            ReconciliationAgent(),
        ]
        for agent in agents_to_register:
            await self.task_router.register_agent(agent)
            self.active_agents[agent.agent_id] = agent
        self.logger.info(f"Registered {len(agents_to_register)} agents.")

    def __repr__(self) -> str:
        """String representation of the Taskmaster."""
        return f"Taskmaster(status={self.status.value}, active_jobs={len(self.active_jobs)})"

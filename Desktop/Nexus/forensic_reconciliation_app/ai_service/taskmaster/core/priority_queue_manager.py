"""
Priority Queue Manager - Priority-Based Job Queue Management

This module implements the PriorityQueueManager class that handles
priority-based job queues with multiple priority levels and strategies.
"""

import asyncio
import logging
import heapq
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json

from ..models.job import Job, JobStatus, JobPriority, JobType


class QueueStrategy(Enum):
    """Queue strategy types."""
    PRIORITY_FIRST = "priority_first"      # Highest priority jobs first
    FAIR_SHARING = "fair_sharing"          # Fair distribution across priorities
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"  # Weighted round-robin
    DEADLINE_AWARE = "deadline_aware"      # Consider job deadlines
    COST_AWARE = "cost_aware"              # Consider job costs
    HYBRID = "hybrid"                      # Hybrid approach


class QueueStatus(Enum):
    """Queue status enumeration."""
    ACTIVE = "active"                      # Queue is active and processing jobs
    PAUSED = "paused"                      # Queue is paused
    DRAINING = "draining"                  # Queue is draining (no new jobs)
    FULL = "full"                          # Queue is at capacity
    ERROR = "error"                        # Queue is in error state


@dataclass
class QueueMetrics:
    """Queue performance metrics."""
    
    total_jobs_processed: int = 0
    jobs_by_priority: Dict[str, int] = field(default_factory=dict)
    average_wait_time: float = 0.0
    average_processing_time: float = 0.0
    queue_length: int = 0
    throughput_per_minute: float = 0.0
    error_rate: float = 0.0
    
    def update_average_wait_time(self, new_wait_time: float):
        """Update average wait time."""
        self.average_wait_time = (
            (self.average_wait_time * self.total_jobs_processed + new_wait_time) /
            (self.total_jobs_processed + 1)
        )
    
    def update_average_processing_time(self, new_processing_time: float):
        """Update average processing time."""
        self.average_processing_time = (
            (self.average_processing_time * self.total_jobs_processed + new_processing_time) /
            (self.total_jobs_processed + 1)
        )


@dataclass
class QueueConfig:
    """Queue configuration."""
    
    name: str
    strategy: QueueStrategy
    max_size: int = 1000
    priority_weights: Dict[str, float] = field(default_factory=dict)
    fair_sharing_quantum: timedelta = timedelta(seconds=30)
    enable_preemption: bool = True
    preemption_threshold: int = 3
    cost_threshold: float = 100.0
    deadline_buffer: timedelta = timedelta(minutes=5)
    
    def __post_init__(self):
        if not self.priority_weights:
            self.priority_weights = {
                JobPriority.CRITICAL.value: 10.0,
                JobPriority.HIGH.value: 7.0,
                JobPriority.MEDIUM.value: 5.0,
                JobPriority.LOW.value: 3.0,
                JobPriority.BATCH.value: 2.0,
                JobPriority.MAINTENANCE.value: 1.0
            }


class PriorityQueue:
    """Priority queue implementation with multiple strategies."""
    
    def __init__(self, config: QueueConfig):
        """Initialize the priority queue."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Queue state
        self.jobs: Dict[str, Job] = {}
        self.priority_queues: Dict[str, List[Job]] = defaultdict(list)
        self.processing_jobs: Dict[str, Job] = {}
        self.completed_jobs: Dict[str, Job] = {}
        self.failed_jobs: Dict[str, Job] = {}
        
        # Queue metrics
        self.metrics = QueueMetrics()
        
        # Strategy-specific state
        self.fair_sharing_counters: Dict[str, int] = defaultdict(int)
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        self.last_processed: Dict[str, datetime] = defaultdict(lambda: datetime.utcnow())
        
        # Queue status
        self.status = QueueStatus.ACTIVE
        
        self.logger.info(f"Priority queue '{config.name}' initialized with strategy: {config.strategy.value}")
    
    async def add_job(self, job: Job) -> bool:
        """Add a job to the queue."""
        try:
            if self.status != QueueStatus.ACTIVE:
                self.logger.warning(f"Cannot add job to queue in {self.status.value} state")
                return False
            
            if len(self.jobs) >= self.config.max_size:
                self.status = QueueStatus.FULL
                self.logger.warning(f"Queue is full, cannot add job {job.id}")
                return False
            
            # Add job to main job list
            self.jobs[job.id] = job
            
            # Add to priority queue
            priority_key = job.priority.value
            self.priority_queues[priority_key].append(job)
            
            # Update metrics
            self.metrics.queue_length = len(self.jobs)
            self.metrics.jobs_by_priority[priority_key] = \
                self.metrics.jobs_by_priority.get(priority_key, 0) + 1
            
            self.logger.info(f"Added job {job.id} with priority {priority_key} to queue")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding job {job.id} to queue: {e}")
            return False
    
    async def get_next_job(self) -> Optional[Job]:
        """Get the next job based on the queue strategy."""
        try:
            if not self.jobs:
                return None
            
            if self.config.strategy == QueueStrategy.PRIORITY_FIRST:
                return await self._get_job_priority_first()
            elif self.config.strategy == QueueStrategy.FAIR_SHARING:
                return await self._get_job_fair_sharing()
            elif self.config.strategy == QueueStrategy.WEIGHTED_ROUND_ROBIN:
                return await self._get_job_weighted_round_robin()
            elif self.config.strategy == QueueStrategy.DEADLINE_AWARE:
                return await self._get_job_deadline_aware()
            elif self.config.strategy == QueueStrategy.COST_AWARE:
                return await self._get_job_cost_aware()
            elif self.config.strategy == QueueStrategy.HYBRID:
                return await self._get_job_hybrid()
            else:
                return await self._get_job_priority_first()
                
        except Exception as e:
            self.logger.error(f"Error getting next job: {e}")
            return None
    
    async def remove_job(self, job_id: str) -> bool:
        """Remove a job from the queue."""
        try:
            if job_id not in self.jobs:
                return False
            
            job = self.jobs[job_id]
            priority_key = job.priority.value
            
            # Remove from main job list
            del self.jobs[job_id]
            
            # Remove from priority queue
            if job_id in [j.id for j in self.priority_queues[priority_key]]:
                self.priority_queues[priority_key] = [
                    j for j in self.priority_queues[priority_key] if j.id != job_id
                ]
            
            # Update metrics
            self.metrics.queue_length = len(self.jobs)
            self.metrics.jobs_by_priority[priority_key] = \
                max(0, self.metrics.jobs_by_priority.get(priority_key, 1) - 1)
            
            self.logger.info(f"Removed job {job_id} from queue")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing job {job_id}: {e}")
            return False
    
    async def mark_job_processing(self, job_id: str):
        """Mark a job as being processed."""
        try:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                self.processing_jobs[job_id] = job
                
                # Calculate wait time
                wait_time = (datetime.utcnow() - job.created_at).total_seconds()
                self.metrics.update_average_wait_time(wait_time)
                
                self.logger.info(f"Marked job {job_id} as processing")
                
        except Exception as e:
            self.logger.error(f"Error marking job {job_id} as processing: {e}")
    
    async def mark_job_completed(self, job_id: str, processing_time: float = None):
        """Mark a job as completed."""
        try:
            if job_id in self.processing_jobs:
                job = self.processing_jobs[job_id]
                
                # Move to completed jobs
                self.completed_jobs[job_id] = job
                del self.processing_jobs[job_id]
                
                # Update metrics
                self.metrics.total_jobs_processed += 1
                if processing_time:
                    self.metrics.update_average_processing_time(processing_time)
                
                self.logger.info(f"Marked job {job_id} as completed")
                
        except Exception as e:
            self.logger.error(f"Error marking job {job_id} as completed: {e}")
    
    async def mark_job_failed(self, job_id: str, error: str = None):
        """Mark a job as failed."""
        try:
            if job_id in self.processing_jobs:
                job = self.processing_jobs[job_id]
                job.last_error = error
                
                # Move to failed jobs
                self.failed_jobs[job_id] = job
                del self.processing_jobs[job_id]
                
                # Update metrics
                self.metrics.total_jobs_processed += 1
                
                self.logger.info(f"Marked job {job_id} as failed: {error}")
                
        except Exception as e:
            self.logger.error(f"Error marking job {job_id} as failed: {e}")
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            'name': self.config.name,
            'strategy': self.config.strategy.value,
            'status': self.status.value,
            'total_jobs': len(self.jobs),
            'processing_jobs': len(self.processing_jobs),
            'completed_jobs': len(self.completed_jobs),
            'failed_jobs': len(self.failed_jobs),
            'priority_distribution': dict(self.metrics.jobs_by_priority),
            'metrics': {
                'average_wait_time': self.metrics.average_wait_time,
                'average_processing_time': self.metrics.average_processing_time,
                'throughput_per_minute': self.metrics.throughput_per_minute,
                'error_rate': self.metrics.error_rate
            }
        }
    
    async def _get_job_priority_first(self) -> Optional[Job]:
        """Get next job using priority-first strategy."""
        try:
            # Get all priorities in order
            priorities = list(self.priority_queues.keys())
            priorities.sort(key=lambda p: self.config.priority_weights.get(p, 0), reverse=True)
            
            for priority in priorities:
                if self.priority_queues[priority]:
                    return self.priority_queues[priority].pop(0)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in priority-first strategy: {e}")
            return None
    
    async def _get_job_fair_sharing(self) -> Optional[Job]:
        """Get next job using fair-sharing strategy."""
        try:
            # Find the priority with the lowest counter
            min_counter = float('inf')
            selected_priority = None
            
            for priority, counter in self.fair_sharing_counters.items():
                if self.priority_queues[priority] and counter < min_counter:
                    min_counter = counter
                    selected_priority = priority
            
            if selected_priority and self.priority_queues[selected_priority]:
                # Increment counter for this priority
                self.fair_sharing_counters[selected_priority] += 1
                
                # Get job from this priority
                job = self.priority_queues[selected_priority].pop(0)
                
                # Reset counter if we've processed enough jobs
                if self.fair_sharing_counters[selected_priority] >= self.config.fair_sharing_quantum.total_seconds():
                    self.fair_sharing_counters[selected_priority] = 0
                
                return job
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in fair-sharing strategy: {e}")
            return None
    
    async def _get_job_weighted_round_robin(self) -> Optional[Job]:
        """Get next job using weighted round-robin strategy."""
        try:
            # Get all priorities with their weights
            priorities = [(p, self.config.priority_weights.get(p, 1.0)) 
                         for p in self.priority_queues.keys() if self.priority_queues[p]]
            
            if not priorities:
                return None
            
            # Sort by weight (descending)
            priorities.sort(key=lambda x: x[1], reverse=True)
            
            # Use round-robin within each priority
            for priority, weight in priorities:
                if self.priority_queues[priority]:
                    # Get job using round-robin
                    queue = self.priority_queues[priority]
                    index = self.round_robin_index[priority] % len(queue)
                    job = queue.pop(index)
                    
                    # Update round-robin index
                    self.round_robin_index[priority] = (index + 1) % len(queue)
                    
                    return job
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in weighted round-robin strategy: {e}")
            return None
    
    async def _get_job_deadline_aware(self) -> Optional[Job]:
        """Get next job using deadline-aware strategy."""
        try:
            # Collect all jobs with deadlines
            jobs_with_deadlines = []
            
            for priority, queue in self.priority_queues.items():
                for job in queue:
                    if hasattr(job, 'deadline') and job.deadline:
                        time_until_deadline = (job.deadline - datetime.utcnow()).total_seconds()
                        if time_until_deadline > 0:
                            jobs_with_deadlines.append((job, time_until_deadline, priority))
            
            if not jobs_with_deadlines:
                # Fall back to priority-first if no deadlines
                return await self._get_job_priority_first()
            
            # Sort by deadline urgency and priority
            jobs_with_deadlines.sort(key=lambda x: (x[1], -self.config.priority_weights.get(x[2], 0)))
            
            # Get the most urgent job
            selected_job, _, priority = jobs_with_deadlines[0]
            
            # Remove from queue
            self.priority_queues[priority] = [
                j for j in self.priority_queues[priority] if j.id != selected_job.id
            ]
            
            return selected_job
            
        except Exception as e:
            self.logger.error(f"Error in deadline-aware strategy: {e}")
            return None
    
    async def _get_job_cost_aware(self) -> Optional[Job]:
        """Get next job using cost-aware strategy."""
        try:
            # Collect all jobs with cost information
            jobs_with_costs = []
            
            for priority, queue in self.priority_queues.items():
                for job in queue:
                    estimated_cost = getattr(job, 'estimated_cost', 0) or 0
                    jobs_with_costs.append((job, estimated_cost, priority))
            
            if not jobs_with_costs:
                return await self._get_job_priority_first()
            
            # Sort by cost efficiency (lower cost = higher priority) and priority
            jobs_with_costs.sort(key=lambda x: (x[1], -self.config.priority_weights.get(x[2], 0)))
            
            # Get the most cost-efficient job
            selected_job, _, priority = jobs_with_costs[0]
            
            # Remove from queue
            self.priority_queues[priority] = [
                j for j in self.priority_queues[priority] if j.id != selected_job.id
            ]
            
            return selected_job
            
        except Exception as e:
            self.logger.error(f"Error in cost-aware strategy: {e}")
            return None
    
    async def _get_job_hybrid(self) -> Optional[Job]:
        """Get next job using hybrid strategy."""
        try:
            # Combine multiple factors: priority, deadline, cost, and fairness
            jobs_scores = []
            
            for priority, queue in self.priority_queues.items():
                for job in queue:
                    score = 0.0
                    
                    # Priority score
                    priority_weight = self.config.priority_weights.get(priority, 1.0)
                    score += priority_weight * 10
                    
                    # Deadline score (if available)
                    if hasattr(job, 'deadline') and job.deadline:
                        time_until_deadline = (job.deadline - datetime.utcnow()).total_seconds()
                        if time_until_deadline > 0:
                            # Higher score for urgent deadlines
                            score += max(0, 100 - time_until_deadline)
                    
                    # Cost score (if available)
                    estimated_cost = getattr(job, 'estimated_cost', 0) or 0
                    if estimated_cost > 0:
                        # Lower cost = higher score
                        score += max(0, 50 - estimated_cost)
                    
                    # Fairness score
                    fairness_counter = self.fair_sharing_counters.get(priority, 0)
                    score += max(0, 20 - fairness_counter)
                    
                    jobs_scores.append((job, score, priority))
            
            if not jobs_scores:
                return None
            
            # Sort by score (descending)
            jobs_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get the highest-scoring job
            selected_job, _, priority = jobs_scores[0]
            
            # Remove from queue
            self.priority_queues[priority] = [
                j for j in self.priority_queues[priority] if j.id != selected_job.id
            ]
            
            # Update fairness counter
            self.fair_sharing_counters[priority] += 1
            
            return selected_job
            
        except Exception as e:
            self.logger.error(f"Error in hybrid strategy: {e}")
            return None
    
    async def pause_queue(self):
        """Pause the queue."""
        self.status = QueueStatus.PAUSED
        self.logger.info("Queue paused")
    
    async def resume_queue(self):
        """Resume the queue."""
        self.status = QueueStatus.ACTIVE
        self.logger.info("Queue resumed")
    
    async def drain_queue(self):
        """Drain the queue (no new jobs, process existing ones)."""
        self.status = QueueStatus.DRAINING
        self.logger.info("Queue draining started")
    
    async def clear_queue(self):
        """Clear all jobs from the queue."""
        self.jobs.clear()
        self.priority_queues.clear()
        self.processing_jobs.clear()
        self.completed_jobs.clear()
        self.failed_jobs.clear()
        
        # Reset metrics
        self.metrics.queue_length = 0
        self.metrics.jobs_by_priority.clear()
        
        self.logger.info("Queue cleared")


class PriorityQueueManager:
    """
    Manager for multiple priority queues.
    
    The PriorityQueueManager is responsible for:
    - Managing multiple priority queues
    - Distributing jobs across queues
    - Monitoring queue performance
    - Balancing load between queues
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the PriorityQueueManager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.default_queue_config = config.get('default_queue_config', {})
        self.enable_load_balancing = config.get('enable_load_balancing', True)
        self.load_balancing_threshold = config.get('load_balancing_threshold', 0.8)
        
        # Internal state
        self.queues: Dict[str, PriorityQueue] = {}
        self.queue_routing: Dict[str, str] = {}  # job_type -> queue_name
        self.queue_metrics: Dict[str, QueueMetrics] = {}
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info("PriorityQueueManager initialized successfully")
    
    async def start(self):
        """Start the PriorityQueueManager."""
        self.logger.info("Starting PriorityQueueManager...")
        
        # Initialize default queues
        await self._initialize_default_queues()
        
        # Start background tasks
        asyncio.create_task(self._monitor_queue_performance())
        asyncio.create_task(self._balance_queue_load())
        
        self.logger.info("PriorityQueueManager started successfully")
    
    async def stop(self):
        """Stop the PriorityQueueManager."""
        self.logger.info("Stopping PriorityQueueManager...")
        self.logger.info("PriorityQueueManager stopped")
    
    async def create_queue(self, name: str, config: QueueConfig) -> bool:
        """Create a new priority queue."""
        try:
            if name in self.queues:
                self.logger.warning(f"Queue '{name}' already exists")
                return False
            
            queue = PriorityQueue(config)
            self.queues[name] = queue
            self.queue_metrics[name] = QueueMetrics()
            
            self.logger.info(f"Created queue '{name}' with strategy {config.strategy.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating queue '{name}': {e}")
            return False
    
    async def remove_queue(self, name: str) -> bool:
        """Remove a priority queue."""
        try:
            if name not in self.queues:
                return False
            
            # Drain and clear the queue
            await self.queues[name].drain_queue()
            await self.queues[name].clear_queue()
            
            # Remove queue
            del self.queues[name]
            if name in self.queue_metrics:
                del self.queue_metrics[name]
            
            # Remove routing rules
            self.queue_routing = {k: v for k, v in self.queue_routing.items() if v != name}
            
            self.logger.info(f"Removed queue '{name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing queue '{name}': {e}")
            return False
    
    async def add_job(self, job: Job, queue_name: str = None) -> bool:
        """Add a job to a specific queue or auto-route."""
        try:
            if not queue_name:
                queue_name = await self._route_job_to_queue(job)
            
            if not queue_name or queue_name not in self.queues:
                self.logger.error(f"Invalid queue name: {queue_name}")
                return False
            
            success = await self.queues[queue_name].add_job(job)
            if success:
                self.logger.info(f"Added job {job.id} to queue '{queue_name}'")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error adding job {job.id}: {e}")
            return False
    
    async def get_next_job(self, queue_name: str = None) -> Optional[Tuple[str, Job]]:
        """Get the next job from a specific queue or find the best one."""
        try:
            if queue_name:
                if queue_name not in self.queues:
                    return None
                
                job = await self.queues[queue_name].get_next_job()
                if job:
                    return queue_name, job
                
                return None
            
            # Find the best queue with available jobs
            best_queue = await self._find_best_queue()
            if best_queue:
                job = await self.queues[best_queue].get_next_job()
                if job:
                    return best_queue, job
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting next job: {e}")
            return None
    
    async def get_queue_status(self, queue_name: str = None) -> Dict[str, Any]:
        """Get status of specific queue or all queues."""
        try:
            if queue_name:
                if queue_name not in self.queues:
                    return {}
                
                return await self.queues[queue_name].get_queue_status()
            
            # Get status of all queues
            all_status = {}
            for name, queue in self.queues.items():
                all_status[name] = await queue.get_queue_status()
            
            return all_status
            
        except Exception as e:
            self.logger.error(f"Error getting queue status: {e}")
            return {}
    
    async def set_queue_routing(self, job_type: str, queue_name: str):
        """Set routing rule for a job type."""
        try:
            if queue_name not in self.queues:
                self.logger.error(f"Queue '{queue_name}' does not exist")
                return False
            
            self.queue_routing[job_type] = queue_name
            self.logger.info(f"Set routing: {job_type} -> {queue_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting queue routing: {e}")
            return False
    
    async def _initialize_default_queues(self):
        """Initialize default priority queues."""
        try:
            # High-priority queue for critical jobs
            high_priority_config = QueueConfig(
                name="high_priority",
                strategy=QueueStrategy.PRIORITY_FIRST,
                max_size=100,
                priority_weights={
                    JobPriority.CRITICAL.value: 10.0,
                    JobPriority.HIGH.value: 7.0
                }
            )
            await self.create_queue("high_priority", high_priority_config)
            
            # Standard queue for normal jobs
            standard_config = QueueConfig(
                name="standard",
                strategy=QueueStrategy.WEIGHTED_ROUND_ROBIN,
                max_size=500,
                priority_weights={
                    JobPriority.MEDIUM.value: 5.0,
                    JobPriority.LOW.value: 3.0
                }
            )
            await self.create_queue("standard", standard_config)
            
            # Batch queue for batch processing
            batch_config = QueueConfig(
                name="batch",
                strategy=QueueStrategy.FAIR_SHARING,
                max_size=200,
                priority_weights={
                    JobPriority.BATCH.value: 2.0,
                    JobPriority.MAINTENANCE.value: 1.0
                }
            )
            await self.create_queue("batch", batch_config)
            
            # Set default routing
            await self.set_queue_routing(JobType.EVIDENCE_COLLECTION.value, "high_priority")
            await self.set_queue_routing(JobType.FRAUD_DETECTION.value, "high_priority")
            await self.set_queue_routing(JobType.BATCH_PROCESSING.value, "batch")
            
        except Exception as e:
            self.logger.error(f"Error initializing default queues: {e}")
    
    async def _route_job_to_queue(self, job: Job) -> Optional[str]:
        """Route a job to the appropriate queue."""
        try:
            # Check explicit routing rules
            if job.job_type.value in self.queue_routing:
                return self.queue_routing[job.job_type.value]
            
            # Route by priority
            if job.priority in [JobPriority.CRITICAL, JobPriority.HIGH]:
                return "high_priority"
            elif job.priority in [JobPriority.BATCH, JobPriority.MAINTENANCE]:
                return "batch"
            else:
                return "standard"
            
        except Exception as e:
            self.logger.error(f"Error routing job {job.id}: {e}")
            return "standard"
    
    async def _find_best_queue(self) -> Optional[str]:
        """Find the best queue with available jobs."""
        try:
            available_queues = []
            
            for name, queue in self.queues.items():
                if queue.status == QueueStatus.ACTIVE and queue.jobs:
                    # Calculate queue score based on load and performance
                    load_factor = len(queue.jobs) / queue.config.max_size
                    performance_score = 1.0 - queue.metrics.error_rate
                    
                    queue_score = (1.0 - load_factor) * performance_score
                    available_queues.append((name, queue_score))
            
            if not available_queues:
                return None
            
            # Return the queue with the best score
            available_queues.sort(key=lambda x: x[1], reverse=True)
            return available_queues[0][0]
            
        except Exception as e:
            self.logger.error(f"Error finding best queue: {e}")
            return None
    
    async def _monitor_queue_performance(self):
        """Monitor performance of all queues."""
        while True:
            try:
                for name, queue in self.queues.items():
                    # Update queue metrics
                    status = await queue.get_queue_status()
                    
                    if name in self.queue_metrics:
                        metrics = self.queue_metrics[name]
                        metrics.queue_length = status.get('total_jobs', 0)
                        metrics.total_jobs_processed = status.get('metrics', {}).get('total_jobs_processed', 0)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring queue performance: {e}")
                await asyncio.sleep(60)
    
    async def _balance_queue_load(self):
        """Balance load between queues."""
        while True:
            try:
                if not self.enable_load_balancing:
                    await asyncio.sleep(300)
                    continue
                
                # Check for overloaded queues
                for name, queue in self.queues.items():
                    load_factor = len(queue.jobs) / queue.config.max_size
                    
                    if load_factor > self.load_balancing_threshold:
                        await self._redistribute_queue_load(name)
                
                await asyncio.sleep(300)  # Balance every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error balancing queue load: {e}")
                await asyncio.sleep(300)
    
    async def _redistribute_queue_load(self, overloaded_queue_name: str):
        """Redistribute load from an overloaded queue."""
        try:
            overloaded_queue = self.queues[overloaded_queue_name]
            
            # Find underloaded queues
            underloaded_queues = []
            for name, queue in self.queues.items():
                if name != overloaded_queue_name:
                    load_factor = len(queue.jobs) / queue.config.max_size
                    if load_factor < 0.5:  # Under 50% load
                        underloaded_queues.append((name, queue))
            
            if not underloaded_queues:
                return
            
            # Sort underloaded queues by available capacity
            underloaded_queues.sort(key=lambda x: x[1].config.max_size - len(x[1].jobs), reverse=True)
            
            # Move some jobs to underloaded queues
            jobs_to_move = min(5, len(overloaded_queue.jobs) // 4)  # Move up to 25% of jobs
            
            for i in range(jobs_to_move):
                if not overloaded_queue.jobs:
                    break
                
                # Get a job (preferably lower priority)
                job = None
                for priority in [JobPriority.LOW, JobPriority.MEDIUM, JobPriority.HIGH]:
                    if priority.value in overloaded_queue.priority_queues and overloaded_queue.priority_queues[priority.value]:
                        job = overloaded_queue.priority_queues[priority.value].pop(0)
                        break
                
                if job:
                    # Find the best underloaded queue
                    target_queue = underloaded_queues[0][0]
                    
                    # Remove from overloaded queue
                    await overloaded_queue.remove_job(job.id)
                    
                    # Add to target queue
                    await self.queues[target_queue].add_job(job)
                    
                    self.logger.info(f"Moved job {job.id} from '{overloaded_queue_name}' to '{target_queue}' for load balancing")
            
        except Exception as e:
            self.logger.error(f"Error redistributing queue load: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'default_queue_config': {},
        'enable_load_balancing': True,
        'load_balancing_threshold': 0.8
    }
    
    # Initialize priority queue manager
    manager = PriorityQueueManager(config)
    
    print("PriorityQueueManager system initialized successfully!")

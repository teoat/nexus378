"""
Job Scheduler - Intelligent Job Assignment and Scheduling Engine

This module implements the JobScheduler class that handles intelligent job
assignment, priority management, and resource optimization for the Taskmaster system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq
import uuid

from ..models.job import Job, JobStatus, JobPriority, JobType
from ..models.agent import Agent, AgentStatus, AgentType
from ..models.queue import Queue, QueueType, QueueStatus


class SchedulingAlgorithm(Enum):
    """Scheduling algorithm types."""
    PRIORITY_FIRST = "priority_first"
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    PRIORITY_WEIGHTED_ROUND_ROBIN = "priority_weighted_round_robin"
    FAIR_SHARE = "fair_share"
    DEADLINE_ORIENTED = "deadline_oriented"
    RESOURCE_AWARE = "resource_aware"
    MACHINE_LEARNING = "machine_learning"


class PreemptionPolicy(Enum):
    """Job preemption policies."""
    NONE = "none"
    PRIORITY_ONLY = "priority_only"
    RESOURCE_AWARE = "resource_aware"
    AGGRESSIVE = "aggressive"


@dataclass
class SchedulingMetrics:
    """Metrics for scheduling performance."""
    
    total_jobs_scheduled: int = 0
    total_jobs_completed: int = 0
    total_jobs_failed: int = 0
    average_scheduling_time: float = 0.0
    average_completion_time: float = 0.0
    resource_utilization: float = 0.0
    queue_wait_times: Dict[str, float] = field(default_factory=dict)
    preemption_count: int = 0
    fairness_score: float = 0.0
    
    def update_average_scheduling_time(self, new_time: float):
        """Update average scheduling time."""
        self.average_scheduling_time = (
            (self.average_scheduling_time * self.total_jobs_scheduled + new_time) /
            (self.total_jobs_scheduled + 1)
        )
    
    def update_average_completion_time(self, new_time: float):
        """Update average completion time."""
        self.average_completion_time = (
            (self.average_completion_time * self.total_jobs_completed + new_time) /
            (self.total_jobs_completed + 1)
        )


class JobScheduler:
    """
    Intelligent job scheduler for the Taskmaster system.
    
    The JobScheduler is responsible for:
    - Assigning jobs to available agents
    - Managing job priorities and preemption
    - Optimizing resource utilization
    - Implementing various scheduling algorithms
    - Monitoring scheduling performance
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the JobScheduler."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Scheduling configuration
        self.algorithm = SchedulingAlgorithm(config.get('algorithm', 'priority_weighted_round_robin'))
        self.preemption_policy = PreemptionPolicy(config.get('preemption_policy', 'priority_only'))
        self.fairness_factor = config.get('fairness_factor', 0.8)
        self.max_concurrent_jobs = config.get('max_concurrent_jobs', 1000)
        self.job_timeout = timedelta(seconds=config.get('job_timeout_seconds', 86400))
        
        # Internal state
        self.job_queues: Dict[JobPriority, deque] = defaultdict(deque)
        self.running_jobs: Dict[str, Job] = {}
        self.agent_assignments: Dict[str, List[str]] = defaultdict(list)
        self.job_history: List[Job] = []
        
        # Scheduling metrics
        self.metrics = SchedulingMetrics()
        
        # Algorithm-specific state
        self.round_robin_index = 0
        self.agent_weights: Dict[str, float] = {}
        self.fair_share_quotas: Dict[str, float] = {}
        
        # Performance tracking
        self.scheduling_times: List[float] = []
        self.completion_times: List[float] = []
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info(f"JobScheduler initialized with algorithm: {self.algorithm}")
    
    async def start(self):
        """Start the JobScheduler."""
        self.logger.info("Starting JobScheduler...")
        
        # Initialize agent weights
        await self._initialize_agent_weights()
        
        # Start background tasks
        asyncio.create_task(self._monitor_job_timeouts())
        asyncio.create_task(self._update_scheduling_metrics())
        asyncio.create_task(self._optimize_resource_allocation())
        
        self.logger.info("JobScheduler started successfully")
    
    async def stop(self):
        """Stop the JobScheduler."""
        self.logger.info("Stopping JobScheduler...")
        
        # Cancel all running jobs
        for job_id in list(self.running_jobs.keys()):
            await self._cancel_job(job_id)
        
        self.logger.info("JobScheduler stopped")
    
    async def submit_job(self, job: Job) -> bool:
        """Submit a new job for scheduling."""
        try:
            self.logger.info(f"Submitting job {job.id} with priority {job.priority}")
            
            # Validate job
            if not self._validate_job(job):
                self.logger.error(f"Job {job.id} validation failed")
                return False
            
            # Add to appropriate queue
            self.job_queues[job.priority].append(job)
            
            # Update metrics
            self.metrics.total_jobs_scheduled += 1
            
            # Trigger scheduling
            asyncio.create_task(self._schedule_jobs())
            
            self.logger.info(f"Job {job.id} submitted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting job {job.id}: {e}")
            return False
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running or queued job."""
        try:
            self.logger.info(f"Cancelling job {job_id}")
            
            # Check if job is running
            if job_id in self.running_jobs:
                return await self._cancel_running_job(job_id)
            
            # Check if job is in queue
            for queue in self.job_queues.values():
                for job in queue:
                    if job.id == job_id:
                        queue.remove(job)
                        self.logger.info(f"Job {job_id} removed from queue")
                        return True
            
            self.logger.warning(f"Job {job_id} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling job {job_id}: {e}")
            return False
    
    async def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a specific job."""
        # Check running jobs
        if job_id in self.running_jobs:
            return self.running_jobs[job_id].status
        
        # Check queued jobs
        for queue in self.job_queues.values():
            for job in queue:
                if job.id == job_id:
                    return job.status
        
        # Check job history
        for job in self.job_history:
            if job.id == job_id:
                return job.status
        
        return None
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get the current status of all job queues."""
        status = {
            'algorithm': self.algorithm.value,
            'preemption_policy': self.preemption_policy.value,
            'total_running': len(self.running_jobs),
            'total_queued': sum(len(queue) for queue in self.job_queues.values()),
            'queues': {}
        }
        
        for priority, queue in self.job_queues.items():
            status['queues'][priority.value] = {
                'size': len(queue),
                'oldest_job': queue[0].created_at if queue else None,
                'newest_job': queue[-1].created_at if queue else None
            }
        
        return status
    
    async def get_scheduling_metrics(self) -> SchedulingMetrics:
        """Get current scheduling performance metrics."""
        return self.metrics
    
    async def _schedule_jobs(self):
        """Main scheduling loop."""
        try:
            while True:
                # Get available agents
                available_agents = await self._get_available_agents()
                
                if not available_agents:
                    await asyncio.sleep(1)
                    continue
                
                # Schedule jobs based on algorithm
                jobs_scheduled = 0
                
                if self.algorithm == SchedulingAlgorithm.PRIORITY_FIRST:
                    jobs_scheduled = await self._schedule_priority_first(available_agents)
                elif self.algorithm == SchedulingAlgorithm.ROUND_ROBIN:
                    jobs_scheduled = await self._schedule_round_robin(available_agents)
                elif self.algorithm == SchedulingAlgorithm.WEIGHTED_ROUND_ROBIN:
                    jobs_scheduled = await self._schedule_weighted_round_robin(available_agents)
                elif self.algorithm == SchedulingAlgorithm.PRIORITY_WEIGHTED_ROUND_ROBIN:
                    jobs_scheduled = await self._schedule_priority_weighted_round_robin(available_agents)
                elif self.algorithm == SchedulingAlgorithm.FAIR_SHARE:
                    jobs_scheduled = await self._schedule_fair_share(available_agents)
                elif self.algorithm == SchedulingAlgorithm.DEADLINE_ORIENTED:
                    jobs_scheduled = await self._schedule_deadline_oriented(available_agents)
                elif self.algorithm == SchedulingAlgorithm.RESOURCE_AWARE:
                    jobs_scheduled = await self._schedule_resource_aware(available_agents)
                elif self.algorithm == SchedulingAlgorithm.MACHINE_LEARNING:
                    jobs_scheduled = await self._schedule_machine_learning(available_agents)
                
                if jobs_scheduled == 0:
                    await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error in scheduling loop: {e}")
    
    async def _schedule_priority_first(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using priority-first algorithm."""
        jobs_scheduled = 0
        
        # Sort priorities (HIGH > MEDIUM > LOW)
        priorities = [JobPriority.HIGH, JobPriority.MEDIUM, JobPriority.LOW]
        
        for priority in priorities:
            if not self.job_queues[priority]:
                continue
            
            for agent in available_agents:
                if not self.job_queues[priority]:
                    break
                
                if await self._can_agent_handle_job(agent, self.job_queues[priority][0]):
                    job = self.job_queues[priority].popleft()
                    if await self._assign_job_to_agent(job, agent):
                        jobs_scheduled += 1
                        available_agents.remove(agent)
                        break
        
        return jobs_scheduled
    
    async def _schedule_round_robin(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using round-robin algorithm."""
        jobs_scheduled = 0
        
        for agent in available_agents:
            # Find a job for this agent
            job = await self._find_job_for_agent(agent)
            if job:
                if await self._assign_job_to_agent(job, agent):
                    jobs_scheduled += 1
                    available_agents.remove(agent)
        
        return jobs_scheduled
    
    async def _schedule_weighted_round_robin(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using weighted round-robin algorithm."""
        jobs_scheduled = 0
        
        # Sort agents by weight
        sorted_agents = sorted(available_agents, key=lambda a: self.agent_weights.get(a.id, 1.0), reverse=True)
        
        for agent in sorted_agents:
            job = await self._find_job_for_agent(agent)
            if job:
                if await self._assign_job_to_agent(job, agent):
                    jobs_scheduled += 1
                    available_agents.remove(agent)
        
        return jobs_scheduled
    
    async def _schedule_priority_weighted_round_robin(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using priority-weighted round-robin algorithm."""
        jobs_scheduled = 0
        
        # First, schedule high-priority jobs
        high_priority_scheduled = await self._schedule_priority_first(available_agents)
        jobs_scheduled += high_priority_scheduled
        
        # Then, schedule remaining jobs using weighted round-robin
        remaining_scheduled = await self._schedule_weighted_round_robin(available_agents)
        jobs_scheduled += remaining_scheduled
        
        return jobs_scheduled
    
    async def _schedule_fair_share(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using fair-share algorithm."""
        jobs_scheduled = 0
        
        # Calculate fair share quotas
        await self._update_fair_share_quotas(available_agents)
        
        # Sort agents by their quota usage
        sorted_agents = sorted(available_agents, key=lambda a: self.fair_share_quotas.get(a.id, 0.0))
        
        for agent in sorted_agents:
            job = await self._find_job_for_agent(agent)
            if job:
                if await self._assign_job_to_agent(job, agent):
                    jobs_scheduled += 1
                    available_agents.remove(agent)
                    # Update quota usage
                    self.fair_share_quotas[agent.id] = self.fair_share_quotas.get(agent.id, 0.0) + 1.0
        
        return jobs_scheduled
    
    async def _schedule_deadline_oriented(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using deadline-oriented algorithm."""
        jobs_scheduled = 0
        
        # Collect all jobs with deadlines
        deadline_jobs = []
        for priority, queue in self.job_queues.items():
            for job in queue:
                if hasattr(job, 'deadline') and job.deadline:
                    deadline_jobs.append((job, priority))
        
        # Sort by deadline
        deadline_jobs.sort(key=lambda x: x[0].deadline)
        
        for job, priority in deadline_jobs:
            if not available_agents:
                break
            
            # Find best agent for this job
            best_agent = await self._find_best_agent_for_job(job, available_agents)
            if best_agent:
                if await self._assign_job_to_agent(job, best_agent):
                    jobs_scheduled += 1
                    available_agents.remove(best_agent)
                    # Remove job from queue
                    self.job_queues[priority].remove(job)
        
        return jobs_scheduled
    
    async def _schedule_resource_aware(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using resource-aware algorithm."""
        jobs_scheduled = 0
        
        # Sort agents by resource availability
        sorted_agents = sorted(available_agents, key=lambda a: a.available_resources.get('cpu', 0) + a.available_resources.get('memory', 0), reverse=True)
        
        for agent in sorted_agents:
            # Find job that best fits agent's resources
            job = await self._find_best_fitting_job(agent)
            if job:
                if await self._assign_job_to_agent(job, agent):
                    jobs_scheduled += 1
                    available_agents.remove(agent)
        
        return jobs_scheduled
    
    async def _schedule_machine_learning(self, available_agents: List[Agent]) -> int:
        """Schedule jobs using machine learning algorithm."""
        # This is a placeholder for ML-based scheduling
        # In a real implementation, this would use trained models to predict
        # job completion times and optimal agent assignments
        
        self.logger.info("ML-based scheduling not yet implemented, falling back to priority-first")
        return await self._schedule_priority_first(available_agents)
    
    async def _assign_job_to_agent(self, job: Job, agent: Agent) -> bool:
        """Assign a job to an agent."""
        try:
            # Update job status
            job.status = JobStatus.RUNNING
            job.assigned_agent_id = agent.id
            job.started_at = datetime.utcnow()
            
            # Add to running jobs
            self.running_jobs[job.id] = job
            
            # Update agent assignments
            self.agent_assignments[agent.id].append(job.id)
            
            # Update agent status
            agent.status = AgentStatus.BUSY
            agent.current_job_id = job.id
            
            # Send job to agent (this would be implemented based on your agent communication system)
            # await self._send_job_to_agent(job, agent)
            
            self.logger.info(f"Job {job.id} assigned to agent {agent.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error assigning job {job.id} to agent {agent.id}: {e}")
            return False
    
    async def _can_agent_handle_job(self, agent: Agent, job: Job) -> bool:
        """Check if an agent can handle a specific job."""
        # Check agent type compatibility
        if job.required_agent_type and agent.agent_type != job.required_agent_type:
            return False
        
        # Check resource requirements
        if job.resource_requirements:
            for resource, required in job.resource_requirements.items():
                available = agent.available_resources.get(resource, 0)
                if available < required:
                    return False
        
        # Check agent status
        if agent.status != AgentStatus.AVAILABLE:
            return False
        
        return True
    
    async def _find_job_for_agent(self, agent: Agent) -> Optional[Job]:
        """Find a suitable job for an agent."""
        # Try to find a job that matches the agent's capabilities
        for priority in [JobPriority.HIGH, JobPriority.MEDIUM, JobPriority.LOW]:
            for job in self.job_queues[priority]:
                if await self._can_agent_handle_job(agent, job):
                    return job
        
        return None
    
    async def _find_best_agent_for_job(self, job: Job, available_agents: List[Agent]) -> Optional[Agent]:
        """Find the best agent for a specific job."""
        best_agent = None
        best_score = -1
        
        for agent in available_agents:
            if not await self._can_agent_handle_job(agent, job):
                continue
            
            # Calculate agent score based on various factors
            score = await self._calculate_agent_score(agent, job)
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    async def _find_best_fitting_job(self, agent: Agent) -> Optional[Job]:
        """Find the job that best fits an agent's resources."""
        best_job = None
        best_fit_score = -1
        
        for priority in [JobPriority.HIGH, JobPriority.MEDIUM, JobPriority.LOW]:
            for job in self.job_queues[priority]:
                if not await self._can_agent_handle_job(agent, job):
                    continue
                
                # Calculate fit score based on resource utilization
                fit_score = await self._calculate_resource_fit_score(agent, job)
                
                if fit_score > best_fit_score:
                    best_fit_score = fit_score
                    best_job = job
        
        return best_job
    
    async def _calculate_agent_score(self, agent: Agent, job: Job) -> float:
        """Calculate a score for agent-job compatibility."""
        score = 0.0
        
        # Agent type compatibility
        if agent.agent_type == job.required_agent_type:
            score += 10.0
        
        # Resource availability
        if job.resource_requirements:
            resource_score = 0.0
            for resource, required in job.resource_requirements.items():
                available = agent.available_resources.get(resource, 0)
                if available >= required:
                    resource_score += (available - required) / available
            score += resource_score * 5.0
        
        # Agent performance history
        if hasattr(agent, 'success_rate'):
            score += agent.success_rate * 3.0
        
        # Agent load
        current_load = len(self.agent_assignments.get(agent.id, []))
        score -= current_load * 0.5
        
        return score
    
    async def _calculate_resource_fit_score(self, agent: Agent, job: Job) -> float:
        """Calculate how well a job fits an agent's resources."""
        if not job.resource_requirements:
            return 1.0
        
        total_score = 0.0
        total_resources = 0
        
        for resource, required in job.resource_requirements.items():
            available = agent.available_resources.get(resource, 0)
            if available > 0:
                utilization = required / available
                # Prefer jobs that utilize 70-90% of available resources
                if 0.7 <= utilization <= 0.9:
                    score = 1.0
                elif utilization < 0.7:
                    score = utilization / 0.7
                else:
                    score = 1.0 - (utilization - 0.9) / 0.1
                
                total_score += score
                total_resources += 1
        
        return total_score / total_resources if total_resources > 0 else 0.0
    
    async def _get_available_agents(self) -> List[Agent]:
        """Get list of available agents."""
        # This would be implemented based on your agent management system
        # For now, return an empty list
        return []
    
    async def _initialize_agent_weights(self):
        """Initialize agent weights for weighted scheduling."""
        # This would be implemented based on your agent management system
        pass
    
    async def _update_fair_share_quotas(self, available_agents: List[Agent]):
        """Update fair share quotas for agents."""
        # This would be implemented based on your agent management system
        pass
    
    async def _cancel_running_job(self, job_id: str) -> bool:
        """Cancel a currently running job."""
        try:
            job = self.running_jobs.get(job_id)
            if not job:
                return False
            
            # Update job status
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            
            # Remove from running jobs
            del self.running_jobs[job_id]
            
            # Update agent
            if job.assigned_agent_id:
                agent_id = job.assigned_agent_id
                if job_id in self.agent_assignments[agent_id]:
                    self.agent_assignments[agent_id].remove(job_id)
                
                # Mark agent as available
                # This would update the agent status in your agent management system
            
            # Add to history
            self.job_history.append(job)
            
            self.logger.info(f"Job {job_id} cancelled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling running job {job_id}: {e}")
            return False
    
    async def _cancel_job(self, job_id: str) -> bool:
        """Cancel a job (generic method)."""
        return await self.cancel_job(job_id)
    
    def _validate_job(self, job: Job) -> bool:
        """Validate a job before scheduling."""
        if not job.id:
            return False
        
        if not job.type:
            return False
        
        if not job.priority:
            return False
        
        if job.status != JobStatus.PENDING:
            return False
        
        return True
    
    async def _monitor_job_timeouts(self):
        """Monitor and handle job timeouts."""
        while True:
            try:
                current_time = datetime.utcnow()
                timed_out_jobs = []
                
                for job_id, job in self.running_jobs.items():
                    if job.started_at and (current_time - job.started_at) > self.job_timeout:
                        timed_out_jobs.append(job_id)
                
                for job_id in timed_out_jobs:
                    self.logger.warning(f"Job {job_id} timed out, cancelling")
                    await self.cancel_job(job_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in job timeout monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _update_scheduling_metrics(self):
        """Update scheduling performance metrics."""
        while True:
            try:
                # Update average scheduling time
                if self.scheduling_times:
                    self.metrics.average_scheduling_time = sum(self.scheduling_times) / len(self.scheduling_times)
                
                # Update average completion time
                if self.completion_times:
                    self.metrics.average_completion_time = sum(self.completion_times) / len(self.completion_times)
                
                # Update resource utilization
                total_agents = len(self.agent_assignments)
                busy_agents = len([aid for aid, jobs in self.agent_assignments.items() if jobs])
                self.metrics.resource_utilization = busy_agents / total_agents if total_agents > 0 else 0.0
                
                # Update queue wait times
                for priority, queue in self.job_queues.items():
                    if queue:
                        wait_times = [(datetime.utcnow() - job.created_at).total_seconds() for job in queue]
                        self.metrics.queue_wait_times[priority.value] = sum(wait_times) / len(wait_times)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error updating scheduling metrics: {e}")
                await asyncio.sleep(30)
    
    async def _optimize_resource_allocation(self):
        """Optimize resource allocation based on current load."""
        while True:
            try:
                # Check if we need to scale up or down
                current_load = len(self.running_jobs) / self.max_concurrent_jobs
                
                if current_load > 0.8:  # High load
                    # Consider scaling up
                    self.logger.info("High load detected, considering scale up")
                
                elif current_load < 0.2:  # Low load
                    # Consider scaling down
                    self.logger.info("Low load detected, considering scale down")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in resource optimization: {e}")
                await asyncio.sleep(300)

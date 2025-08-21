"""
Task Router - Intelligent Job Routing Engine

This module implements the TaskRouter class that handles intelligent routing
of jobs to the most suitable agents based on capabilities, workload, and
performance metrics.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import heapq
import math

from ..models.job import Job, JobStatus, JobPriority, JobType
from ..models.agent import Agent, AgentStatus, AgentType
from ..models.queue import Queue, QueueType, QueueStatus


class RoutingStrategy(Enum):
    """Routing strategy types."""
    CAPABILITY_MATCH = "capability_match"
    LOAD_BALANCED = "load_balanced"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COST_AWARE = "cost_aware"
    HYBRID = "hybrid"
    MACHINE_LEARNING = "machine_learning"


class RoutingDecision(Enum):
    """Routing decision types."""
    ROUTE = "route"
    QUEUE = "queue"
    REJECT = "reject"
    SPLIT = "split"
    MERGE = "merge"


@dataclass
class RoutingMetrics:
    """Metrics for routing performance."""
    
    total_jobs_routed: int = 0
    successful_routes: int = 0
    failed_routes: int = 0
    average_routing_time: float = 0.0
    route_accuracy: float = 0.0
    load_distribution_score: float = 0.0
    agent_utilization: Dict[str, float] = field(default_factory=dict)
    
    def update_average_routing_time(self, new_time: float):
        """Update average routing time."""
        self.average_routing_time = (
            (self.average_routing_time * self.total_jobs_routed + new_time) /
            (self.total_jobs_routed + 1)
        )
    
    def update_route_accuracy(self):
        """Update route accuracy."""
        if self.total_jobs_routed > 0:
            self.route_accuracy = self.successful_routes / self.total_jobs_routed


@dataclass
class AgentCapability:
    """Agent capability definition."""
    
    agent_id: str
    agent_type: AgentType
    supported_job_types: List[JobType]
    resource_capacity: Dict[str, float]
    performance_metrics: Dict[str, float]
    specializations: List[str]
    reliability_score: float
    cost_per_hour: float
    last_updated: datetime
    
    def can_handle_job(self, job: Job) -> bool:
        """Check if agent can handle a specific job."""
        # Check job type compatibility
        if job.type not in self.supported_job_types:
            return False
        
        # Check resource requirements
        if job.resource_requirements:
            for resource, required in job.resource_requirements.items():
                available = self.resource_capacity.get(resource, 0)
                if available < required:
                    return False
        
        return True
    
    def calculate_fitness_score(self, job: Job) -> float:
        """Calculate fitness score for a job."""
        score = 0.0
        
        # Base score for capability match
        if self.can_handle_job(job):
            score += 10.0
        
        # Performance score
        if 'throughput' in self.performance_metrics:
            score += self.performance_metrics['throughput'] * 2.0
        
        # Reliability score
        score += self.reliability_score * 5.0
        
        # Specialization bonus
        if hasattr(job, 'specialization') and job.specialization in self.specializations:
            score += 3.0
        
        # Cost efficiency (lower cost = higher score)
        if self.cost_per_hour > 0:
            score += (100.0 / self.cost_per_hour) * 0.1
        
        return score


class TaskRouter:
    """
    Intelligent task router for the Taskmaster system.
    
    The TaskRouter is responsible for:
    - Analyzing job requirements and agent capabilities
    - Making intelligent routing decisions
    - Optimizing resource utilization
    - Implementing various routing strategies
    - Monitoring routing performance
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the TaskRouter."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Routing configuration
        self.strategy = RoutingStrategy(config.get('routing_strategy', 'hybrid'))
        self.max_routing_time = timedelta(seconds=config.get('max_routing_time_seconds', 30))
        self.load_balancing_threshold = config.get('load_balancing_threshold', 0.8)
        self.performance_weight = config.get('performance_weight', 0.4)
        self.cost_weight = config.get('cost_weight', 0.3)
        self.reliability_weight = config.get('reliability_weight', 0.3)
        
        # Internal state
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        self.routing_history: List[Dict[str, Any]] = []
        self.agent_workloads: Dict[str, int] = defaultdict(int)
        self.performance_cache: Dict[str, Dict[str, float]] = {}
        
        # Routing metrics
        self.metrics = RoutingMetrics()
        
        # Strategy-specific state
        self.capability_index: Dict[JobType, List[str]] = defaultdict(list)
        self.performance_rankings: Dict[str, List[str]] = {}
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info(f"TaskRouter initialized with strategy: {self.strategy}")
    
    async def start(self):
        """Start the TaskRouter."""
        self.logger.info("Starting TaskRouter...")
        
        # Initialize agent capabilities
        await self._initialize_agent_capabilities()
        
        # Start background tasks
        asyncio.create_task(self._update_agent_capabilities())
        asyncio.create_task(self._optimize_routing_strategy())
        asyncio.create_task(self._cleanup_routing_history())
        
        self.logger.info("TaskRouter started successfully")
    
    async def stop(self):
        """Stop the TaskRouter."""
        self.logger.info("Stopping TaskRouter...")
        self.logger.info("TaskRouter stopped")
    
    async def route_job(self, job: Job, available_agents: List[Agent]) -> Tuple[RoutingDecision, Optional[str], Dict[str, Any]]:
        """Route a job to the most suitable agent."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Routing job {job.id} with type {job.type}")
            
            # Validate job
            if not self._validate_job_for_routing(job):
                return RoutingDecision.REJECT, None, {"error": "Invalid job for routing"}
            
            # Update metrics
            self.metrics.total_jobs_routed += 1
            
            # Route based on strategy
            if self.strategy == RoutingStrategy.CAPABILITY_MATCH:
                decision, agent_id, metadata = await self._route_capability_match(job, available_agents)
            elif self.strategy == RoutingStrategy.LOAD_BALANCED:
                decision, agent_id, metadata = await self._route_load_balanced(job, available_agents)
            elif self.strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
                decision, agent_id, metadata = await self._route_performance_optimized(job, available_agents)
            elif self.strategy == RoutingStrategy.COST_AWARE:
                decision, agent_id, metadata = await self._route_cost_aware(job, available_agents)
            elif self.strategy == RoutingStrategy.HYBRID:
                decision, agent_id, metadata = await self._route_hybrid(job, available_agents)
            elif self.strategy == RoutingStrategy.MACHINE_LEARNING:
                decision, agent_id, metadata = await self._route_machine_learning(job, available_agents)
            else:
                decision, agent_id, metadata = RoutingDecision.REJECT, None, {"error": "Unknown routing strategy"}
            
            # Update routing history
            routing_record = {
                'job_id': job.id,
                'job_type': job.type,
                'decision': decision.value,
                'agent_id': agent_id,
                'routing_time': (datetime.utcnow() - start_time).total_seconds(),
                'strategy': self.strategy.value,
                'metadata': metadata,
                'timestamp': datetime.utcnow()
            }
            self.routing_history.append(routing_record)
            
            # Update metrics
            routing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update_average_routing_time(routing_time)
            
            if decision == RoutingDecision.ROUTE and agent_id:
                self.metrics.successful_routes += 1
                self._update_agent_workload(agent_id, 1)
            else:
                self.metrics.failed_routes += 1
            
            self.metrics.update_route_accuracy()
            
            self.logger.info(f"Job {job.id} routed with decision: {decision.value}")
            return decision, agent_id, metadata
            
        except Exception as e:
            self.logger.error(f"Error routing job {job.id}: {e}")
            self.metrics.failed_routes += 1
            return RoutingDecision.REJECT, None, {"error": str(e)}
    
    async def get_routing_metrics(self) -> RoutingMetrics:
        """Get current routing performance metrics."""
        return self.metrics
    
    async def get_agent_capabilities(self) -> Dict[str, AgentCapability]:
        """Get current agent capabilities."""
        return self.agent_capabilities
    
    async def update_agent_capability(self, agent_id: str, capability: AgentCapability):
        """Update agent capability information."""
        self.agent_capabilities[agent_id] = capability
        await self._rebuild_capability_index()
        self.logger.info(f"Updated capabilities for agent {agent_id}")
    
    async def _route_capability_match(self, job: Job, available_agents: List[Agent]) -> Tuple[RoutingDecision, Optional[str], Dict[str, Any]]:
        """Route job based on capability matching."""
        suitable_agents = []
        
        for agent in available_agents:
            if agent.id in self.agent_capabilities:
                capability = self.agent_capabilities[agent.id]
                if capability.can_handle_job(job):
                    suitable_agents.append((agent.id, capability.calculate_fitness_score(job)))
        
        if not suitable_agents:
            return RoutingDecision.REJECT, None, {"reason": "No suitable agents found"}
        
        # Sort by fitness score
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        best_agent_id = suitable_agents[0][0]
        
        return RoutingDecision.ROUTE, best_agent_id, {
            "strategy": "capability_match",
            "fitness_score": suitable_agents[0][1],
            "candidates": len(suitable_agents)
        }
    
    async def _route_load_balanced(self, job: Job, available_agents: List[Agent]) -> Tuple[RoutingDecision, Optional[str], Dict[str, Any]]:
        """Route job based on load balancing."""
        suitable_agents = []
        
        for agent in available_agents:
            if agent.id in self.agent_capabilities:
                capability = self.agent_capabilities[agent.id]
                if capability.can_handle_job(job):
                    current_load = self.agent_workloads.get(agent.id, 0)
                    load_score = 1.0 / (1.0 + current_load)  # Lower load = higher score
                    fitness_score = capability.calculate_fitness_score(job)
                    combined_score = (fitness_score * 0.7) + (load_score * 0.3)
                    suitable_agents.append((agent.id, combined_score, current_load))
        
        if not suitable_agents:
            return RoutingDecision.REJECT, None, {"reason": "No suitable agents found"}
        
        # Sort by combined score
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        best_agent_id = suitable_agents[0][0]
        
        return RoutingDecision.ROUTE, best_agent_id, {
            "strategy": "load_balanced",
            "combined_score": suitable_agents[0][1],
            "load_score": suitable_agents[0][2],
            "candidates": len(suitable_agents)
        }
    
    async def _route_performance_optimized(self, job: Job, available_agents: List[Agent]) -> Tuple[RoutingDecision, Optional[str], Dict[str, Any]]:
        """Route job based on performance optimization."""
        suitable_agents = []
        
        for agent in available_agents:
            if agent.id in self.agent_capabilities:
                capability = self.agent_capabilities[agent.id]
                if capability.can_handle_job(job):
                    performance_score = self._calculate_performance_score(agent.id, job)
                    suitable_agents.append((agent.id, performance_score))
        
        if not suitable_agents:
            return RoutingDecision.REJECT, None, {"reason": "No suitable agents found"}
        
        # Sort by performance score
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        best_agent_id = suitable_agents[0][0]
        
        return RoutingDecision.ROUTE, best_agent_id, {
            "strategy": "performance_optimized",
            "performance_score": suitable_agents[0][1],
            "candidates": len(suitable_agents)
        }
    
    async def _route_cost_aware(self, job: Job, available_agents: List[Agent]) -> Tuple[RoutingDecision, Optional[str], Dict[str, Any]]:
        """Route job based on cost awareness."""
        suitable_agents = []
        
        for agent in available_agents:
            if agent.id in self.agent_capabilities:
                capability = self.agent_capabilities[agent.id]
                if capability.can_handle_job(job):
                    cost_score = 1.0 / (1.0 + capability.cost_per_hour)  # Lower cost = higher score
                    fitness_score = capability.calculate_fitness_score(job)
                    combined_score = (fitness_score * 0.6) + (cost_score * 0.4)
                    suitable_agents.append((agent.id, combined_score, capability.cost_per_hour))
        
        if not suitable_agents:
            return RoutingDecision.REJECT, None, {"reason": "No suitable agents found"}
        
        # Sort by combined score
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        best_agent_id = suitable_agents[0][0]
        
        return RoutingDecision.ROUTE, best_agent_id, {
            "strategy": "cost_aware",
            "combined_score": suitable_agents[0][1],
            "cost_per_hour": suitable_agents[0][2],
            "candidates": len(suitable_agents)
        }
    
    async def _route_hybrid(self, job: Job, available_agents: List[Agent]) -> Tuple[RoutingDecision, Optional[str], Dict[str, Any]]:
        """Route job using hybrid approach combining multiple factors."""
        suitable_agents = []
        
        for agent in available_agents:
            if agent.id in self.agent_capabilities:
                capability = self.agent_capabilities[agent.id]
                if capability.can_handle_job(job):
                    # Calculate various scores
                    fitness_score = capability.calculate_fitness_score(job)
                    performance_score = self._calculate_performance_score(agent.id, job)
                    load_score = 1.0 / (1.0 + self.agent_workloads.get(agent.id, 0))
                    cost_score = 1.0 / (1.0 + capability.cost_per_hour)
                    reliability_score = capability.reliability_score
                    
                    # Weighted combination
                    combined_score = (
                        fitness_score * 0.25 +
                        performance_score * self.performance_weight +
                        load_score * 0.15 +
                        cost_score * self.cost_weight +
                        reliability_score * self.reliability_weight
                    )
                    
                    suitable_agents.append((agent.id, combined_score, {
                        'fitness': fitness_score,
                        'performance': performance_score,
                        'load': load_score,
                        'cost': cost_score,
                        'reliability': reliability_score
                    }))
        
        if not suitable_agents:
            return RoutingDecision.REJECT, None, {"reason": "No suitable agents found"}
        
        # Sort by combined score
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        best_agent_id = suitable_agents[0][0]
        
        return RoutingDecision.ROUTE, best_agent_id, {
            "strategy": "hybrid",
            "combined_score": suitable_agents[0][1],
            "score_breakdown": suitable_agents[0][2],
            "candidates": len(suitable_agents)
        }
    
    async def _route_machine_learning(self, job: Job, available_agents: List[Agent]) -> Tuple[RoutingDecision, Optional[str], Dict[str, Any]]:
        """Route job using machine learning approach."""
        # This is a placeholder for ML-based routing
        # In a real implementation, this would use trained models to predict
        # optimal agent assignments based on historical data
        
        self.logger.info("ML-based routing not yet implemented, falling back to hybrid")
        return await self._route_hybrid(job, available_agents)
    
    def _calculate_performance_score(self, agent_id: str, job: Job) -> float:
        """Calculate performance score for an agent and job."""
        if agent_id not in self.agent_capabilities:
            return 0.0
        
        capability = self.agent_capabilities[agent_id]
        
        # Base performance score
        base_score = capability.performance_metrics.get('throughput', 1.0)
        
        # Job type specific performance
        if job.type in capability.performance_metrics:
            job_specific_score = capability.performance_metrics[job.type]
            base_score = (base_score + job_specific_score) / 2.0
        
        # Historical performance from routing history
        historical_score = self._get_historical_performance(agent_id, job.type)
        if historical_score > 0:
            base_score = (base_score + historical_score) / 2.0
        
        return base_score
    
    def _get_historical_performance(self, agent_id: str, job_type: JobType) -> float:
        """Get historical performance for an agent and job type."""
        relevant_history = [
            record for record in self.routing_history
            if record['agent_id'] == agent_id and record['job_type'] == job_type
        ]
        
        if not relevant_history:
            return 0.0
        
        # Calculate success rate
        successful = sum(1 for record in relevant_history if record['decision'] == 'route')
        total = len(relevant_history)
        
        return successful / total if total > 0 else 0.0
    
    def _validate_job_for_routing(self, job: Job) -> bool:
        """Validate job for routing."""
        if not job.id:
            return False
        
        if not job.type:
            return False
        
        if job.status != JobStatus.PENDING:
            return False
        
        return True
    
    def _update_agent_workload(self, agent_id: str, change: int):
        """Update agent workload."""
        self.agent_workloads[agent_id] = max(0, self.agent_workloads[agent_id] + change)
    
    async def _initialize_agent_capabilities(self):
        """Initialize agent capabilities from available agents."""
        # This would be implemented based on your agent management system
        # For now, create some mock capabilities
        pass
    
    async def _rebuild_capability_index(self):
        """Rebuild capability index for efficient lookups."""
        self.capability_index.clear()
        
        for agent_id, capability in self.agent_capabilities.items():
            for job_type in capability.supported_job_types:
                self.capability_index[job_type].append(agent_id)
    
    async def _update_agent_capabilities(self):
        """Periodically update agent capabilities."""
        while True:
            try:
                # This would fetch updated capabilities from your agent management system
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating agent capabilities: {e}")
                await asyncio.sleep(300)
    
    async def _optimize_routing_strategy(self):
        """Optimize routing strategy based on performance."""
        while True:
            try:
                # Analyze routing performance and adjust strategy if needed
                if self.metrics.route_accuracy < 0.8:
                    self.logger.info("Low routing accuracy, considering strategy adjustment")
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                self.logger.error(f"Error optimizing routing strategy: {e}")
                await asyncio.sleep(600)
    
    async def _cleanup_routing_history(self):
        """Clean up old routing history records."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=7)
                
                # Remove old records
                self.routing_history = [
                    record for record in self.routing_history
                    if record['timestamp'] > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up routing history: {e}")
                await asyncio.sleep(3600)


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'routing_strategy': 'hybrid',
        'max_routing_time_seconds': 30,
        'load_balancing_threshold': 0.8,
        'performance_weight': 0.4,
        'cost_weight': 0.3,
        'reliability_weight': 0.3
    }
    
    # Initialize task router
    router = TaskRouter(config)
    
    print("TaskRouter system initialized successfully!")

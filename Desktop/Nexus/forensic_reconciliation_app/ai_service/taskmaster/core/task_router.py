"""
Task Router - Intelligent Job Routing Engine

This module implements the TaskRouter class that provides intelligent
routing of tasks to appropriate agents based on capabilities and load.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..models.job import Job, JobType


class RoutingStrategy(Enum):
    CAPABILITY_MATCH = "capability_match"
    LOAD_BALANCING = "load_balancing"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    COST_AWARE = "cost_aware"
    HYBRID = "hybrid"


@dataclass
class AgentCapability:
    agent_id: str
    capabilities: List[str]
    current_load: float
    performance_score: float
    cost_per_job: float


class TaskRouter:
    """Intelligent task routing engine."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        self.routing_history: List[Dict[str, Any]] = []

    def route_task(self, task: Job) -> Optional[str]:
        """Route a task to the best available agent."""
        try:
            # Get available agents
            available_agents = self._get_available_agents(task)
            if not available_agents:
                return None

            # Apply routing strategy
            strategy = RoutingStrategy(self.config.get("routing_strategy", "hybrid"))

            if strategy == RoutingStrategy.CAPABILITY_MATCH:
                return self._route_by_capability(task, available_agents)
            elif strategy == RoutingStrategy.LOAD_BALANCING:
                return self._route_by_load_balancing(task, available_agents)
            elif strategy == RoutingStrategy.PERFORMANCE_OPTIMIZATION:
                return self._route_by_performance(task, available_agents)
            elif strategy == RoutingStrategy.COST_AWARE:
                return self._route_by_cost(task, available_agents)
            else:  # HYBRID
                return self._route_hybrid(task, available_agents)

        except Exception as e:
            self.logger.error(f"Error routing task: {e}")
            return None

    def _get_available_agents(self, task: Job) -> List[AgentCapability]:
        """Get agents capable of handling the task."""
        available = []
        for agent_id, capability in self.agent_capabilities.items():
            if self._can_handle_task(capability, task):
                available.append(capability)
        return available

    def _can_handle_task(self, capability: AgentCapability, task: Job) -> bool:
        """Check if agent can handle the task."""
        # Check if agent has required capabilities
        task_type = task.job_type.value
        return task_type in capability.capabilities

    def _route_by_capability(self, task: Job, agents: List[AgentCapability]) -> str:
        """Route by best capability match."""
        best_agent = max(
            agents, key=lambda a: len(set(a.capabilities) & {task.job_type.value})
        )
        return best_agent.agent_id

    def _route_by_load_balancing(self, task: Job, agents: List[AgentCapability]) -> str:
        """Route by lowest current load."""
        best_agent = min(agents, key=lambda a: a.current_load)
        return best_agent.agent_id

    def _route_by_performance(self, task: Job, agents: List[AgentCapability]) -> str:
        """Route by highest performance score."""
        best_agent = max(agents, key=lambda a: a.performance_score)
        return best_agent.agent_id

    def _route_by_cost(self, task: Job, agents: List[AgentCapability]) -> str:
        """Route by lowest cost."""
        best_agent = min(agents, key=lambda a: a.cost_per_job)
        return best_agent.agent_id

    def _route_hybrid(self, task: Job, agents: List[AgentCapability]) -> str:
        """Hybrid routing considering multiple factors."""
        # Calculate composite score
        best_score = -1
        best_agent = None

        for agent in agents:
            capability_score = len(set(agent.capabilities) & {task.job_type.value})
            load_score = 1.0 - agent.current_load
            performance_score = agent.performance_score
            cost_score = 1.0 / (1.0 + agent.cost_per_job)

            composite_score = (
                capability_score * 0.4
                + load_score * 0.2
                + performance_score * 0.3
                + cost_score * 0.1
            )

            if composite_score > best_score:
                best_score = composite_score
                best_agent = agent

        return best_agent.agent_id if best_agent else None

    def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        performance_score: float = 1.0,
        cost_per_job: float = 1.0,
    ):
        """Register an agent with its capabilities."""
        self.agent_capabilities[agent_id] = AgentCapability(
            agent_id=agent_id,
            capabilities=capabilities,
            current_load=0.0,
            performance_score=performance_score,
            cost_per_job=cost_per_job,
        )

    def update_agent_load(self, agent_id: str, load: float):
        """Update agent's current load."""
        if agent_id in self.agent_capabilities:
            self.agent_capabilities[agent_id].current_load = load

    def get_agent_capabilities(self) -> Dict[str, AgentCapability]:
        """Get all registered agent capabilities."""
        return self.agent_capabilities.copy()


if __name__ == "__main__":
    router = TaskRouter({"routing_strategy": "hybrid"})
    print("TaskRouter initialized successfully!")

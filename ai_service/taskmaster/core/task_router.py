Task Router - Intelligent Job Routing Engine

This module implements the TaskRouter class that provides intelligent
routing of tasks to appropriate agents based on capabilities and load.

import logging

from ..models.job import Job, JobType

class RoutingStrategy(Enum):

    CAPABILITY_MATCH = "capability_match"
    LOAD_BALANCING = "load_balancing"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    COST_AWARE = "cost_aware"
    HYBRID = "hybrid"

@dataclass

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

if __name__ == "__main__":
    router = TaskRouter({"routing_strategy": "hybrid"})
    print("TaskRouter initialized successfully!")

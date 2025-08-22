"""
Load Balancing Strategies for Taskmaster

Implements various load balancing algorithms to distribute tasks among available agents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLoadBalancer(ABC):
    """Abstract base class for load balancers."""

    def __init__(self, agents: List[Dict[str, Any]]):
        """
        Initializes the load balancer with a list of agents.
        Agents are expected to be dictionaries with at least an 'id' and 'load' metric.
        """
        self.agents = agents

    @abstractmethod
    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Selects the best agent for a given task."""
        pass

    def update_agents(self, agents: List[Dict[str, Any]]):
        """Updates the list of agents."""
        self.agents = agents

class RoundRobinBalancer(BaseLoadBalancer):
    """
    Implements a simple Round Robin load balancing strategy.
    It cycles through the list of agents sequentially.
    """
    def __init__(self, agents: List[Dict[str, Any]]):
        super().__init__(agents)
        self.current_index = 0

    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Selects the next agent in the list."""
        if not self.agents:
            return None

        # Simple round robin logic
        agent = self.agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.agents)

        logger.info(f"RoundRobin: Selected agent {agent['id']} for task {task.get('id', 'N/A')}")
        return agent

class LeastConnectionsBalancer(BaseLoadBalancer):
    """
    Implements a Least Connections load balancing strategy.
    It selects the agent with the lowest current load.
    """
    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Selects the agent with the minimum load."""
        if not self.agents:
            return None

        # Find agent with the minimum load
        best_agent = min(self.agents, key=lambda agent: agent.get('load', 0))

        print(f"LeastConnections: Selected agent {best_agent['id']} with load {best_agent.get('load', 0)} for task {task.get('id', 'N/A')}")
        return best_agent

class WeightedRoundRobinBalancer(BaseLoadBalancer):
    """
    Implements a Weighted Round Robin load balancing strategy.
    Agents with higher weights will receive more tasks.
    This is a placeholder implementation.
    """
    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Selects an agent based on their weight. (Placeholder)"""
        if not self.agents:
            return None

        # Placeholder: just returns the first agent
        print("WeightedRoundRobinBalancer is a placeholder and not fully implemented.")
        agent = self.agents[0]
        print(f"WeightedRoundRobin: Selected agent {agent['id']} for task {task.get('id', 'N/A')}")
        return agent

class IPHashBalancer(BaseLoadBalancer):
    """
    Implements an IP Hash load balancing strategy.
    This ensures that requests from the same client IP are directed to the same agent.
    This is a placeholder implementation.
    """
    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Selects an agent based on a hash of the client IP. (Placeholder)"""
        if not self.agents:
            return None

        client_ip = task.get('client_ip')
        if not client_ip:
            print("IPHashBalancer: 'client_ip' not found in task, falling back to first agent.")
            return self.agents[0]

        # Placeholder: simple hash logic
        hash_val = hash(client_ip)
        agent_index = hash_val % len(self.agents)
        agent = self.agents[agent_index]

        print(f"IPHash: Selected agent {agent['id']} for task {task.get('id', 'N/A')} from IP {client_ip}")
        return agent

class LoadBalancerFactory:
    """Factory to create load balancer instances."""
    @staticmethod
    def create_balancer(strategy: str, agents: List[Dict[str, Any]]) -> BaseLoadBalancer:
        """
        Creates a load balancer based on the given strategy.

        Args:
            strategy: The name of the load balancing strategy.
            agents: The list of agents to balance across.

        Returns:
            An instance of a BaseLoadBalancer subclass.
        """
        if strategy == 'round_robin':
            return RoundRobinBalancer(agents)
        elif strategy == 'least_connections':
            return LeastConnectionsBalancer(agents)
        elif strategy == 'weighted_round_robin':
            return WeightedRoundRobinBalancer(agents)
        elif strategy == 'ip_hash':
            return IPHashBalancer(agents)
        else:
            raise ValueError(f"Unknown load balancing strategy: {strategy}")

# Example usage:
if __name__ == '__main__':
    # Mock agents and tasks
    mock_agents = [
        {'id': 'agent-1', 'load': 10, 'weight': 50},
        {'id': 'agent-2', 'load': 5, 'weight': 30},
        {'id': 'agent-3', 'load': 15, 'weight': 20},
    ]
    mock_task = {'id': 'task-123', 'client_ip': '192.168.1.100'}

    print("--- Testing Load Balancers ---")

    # Round Robin
    rr_balancer = LoadBalancerFactory.create_balancer('round_robin', mock_agents)
    rr_balancer.select_agent(mock_task)
    rr_balancer.select_agent(mock_task)

    # Least Connections
    lc_balancer = LoadBalancerFactory.create_balancer('least_connections', mock_agents)
    lc_balancer.select_agent(mock_task)

    # IP Hash
    ip_balancer = LoadBalancerFactory.create_balancer('ip_hash', mock_agents)
    ip_balancer.select_agent(mock_task)

    # Update IP to show hashing difference
    mock_task_2 = {'id': 'task-456', 'client_ip': '192.168.1.101'}
    ip_balancer.select_agent(mock_task_2)

    print("\n--- Load Balancing Placeholder Implementation Complete ---")

Load Balancing Strategies for Taskmaster

Implements various load balancing algorithms to distribute tasks among available agents.

class BaseLoadBalancer(ABC):

    def __init__(self, agents: List[Dict[str, Any]]):

        Initializes the load balancer with a list of agents.
        Agents are expected to be dictionaries with at least an 'id' and 'load' metric.

        self.agents = agents

    @abstractmethod
    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:

            f"RoundRobin: Selected agent {agent['id']} for task {task.get('id', 'N/A')}"
        )
        return agent

class LeastConnectionsBalancer(BaseLoadBalancer):

    Implements a Least Connections load balancing strategy.
    It selects the agent with the lowest current load.

    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        best_agent = min(self.agents, key=lambda agent: agent.get("load", 0))

        logging.info(
            f"LeastConnections: Selected agent {best_agent['id']} with load {best_agent.get('load', 0)} for task {task.get('id', 'N/A')}"
        )
        return best_agent

class WeightedRoundRobinBalancer(BaseLoadBalancer):

    Implements a Weighted Round Robin load balancing strategy.
    Agents with higher weights will receive more tasks.
    This is a placeholder implementation.

    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        print("WeightedRoundRobinBalancer is a placeholder and not fully implemented.")
        agent = self.agents[0]
        print(
            f"WeightedRoundRobin: Selected agent {agent['id']} for task {task.get('id', 'N/A')}"
        )
        return agent

class IPHashBalancer(BaseLoadBalancer):

    Implements an IP Hash load balancing strategy.
    This ensures that requests from the same client IP are directed to the same agent.
    This is a placeholder implementation.

    def select_agent(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:

        client_ip = task.get("client_ip")
        if not client_ip:
            print(
                "IPHashBalancer: 'client_ip' not found in task, falling back to first agent."
            )
            return self.agents[0]

        # Placeholder: simple hash logic
        hash_val = hash(client_ip)
        agent_index = hash_val % len(self.agents)
        agent = self.agents[agent_index]

        print(
            f"IPHash: Selected agent {agent['id']} for task {task.get('id', 'N/A')} from IP {client_ip}"
        )
        return agent

class LoadBalancerFactory:

        if strategy == "round_robin":
            return RoundRobinBalancer(agents)
        elif strategy == "least_connections":
            return LeastConnectionsBalancer(agents)
        elif strategy == "weighted_round_robin":
            return WeightedRoundRobinBalancer(agents)
        elif strategy == "ip_hash":
            return IPHashBalancer(agents)
        else:
            raise ValueError(f"Unknown load balancing strategy: {strategy}")

# Example usage:
if __name__ == "__main__":
    # Mock agents and tasks
    mock_agents = [
        {"id": "agent-1", "load": 10, "weight": 50},
        {"id": "agent-2", "load": 5, "weight": 30},
        {"id": "agent-3", "load": 15, "weight": 20},
    ]
    mock_task = {"id": "task-123", "client_ip": "192.168.1.100"}

    print("--- Testing Load Balancers ---")

    # Round Robin
    rr_balancer = LoadBalancerFactory.create_balancer("round_robin", mock_agents)
    rr_balancer.select_agent(mock_task)
    rr_balancer.select_agent(mock_task)

    # Least Connections
    lc_balancer = LoadBalancerFactory.create_balancer("least_connections", mock_agents)
    lc_balancer.select_agent(mock_task)

    # IP Hash
    ip_balancer = LoadBalancerFactory.create_balancer("ip_hash", mock_agents)
    ip_balancer.select_agent(mock_task)

    # Update IP to show hashing difference
    mock_task_2 = {"id": "task-456", "client_ip": "192.168.1.101"}
    ip_balancer.select_agent(mock_task_2)

    print("\n--- Load Balancing Placeholder Implementation Complete ---")

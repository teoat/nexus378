"""
Load Balancing Strategies Implementation
Implements advanced load balancing for optimal agent distribution
"""

import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Available load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASH = "consistent_hash"
    ADAPTIVE = "adaptive"


@dataclass
class AgentMetrics:
    """Agent performance and load metrics"""
    agent_id: str
    current_load: int
    total_capacity: int
    response_time: float  # milliseconds
    success_rate: float
    last_heartbeat: datetime
    health_score: float
    task_history: List[Dict[str, Any]]


@dataclass
class LoadBalancingDecision:
    """Result of load balancing decision"""
    selected_agent_id: str
    strategy_used: LoadBalancingStrategy
    reasoning: str
    confidence_score: float
    alternative_agents: List[str]


class LoadBalancer:
    """Advanced load balancing system for Taskmaster agents"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE):
        self.strategy = strategy
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.last_round_robin_index = 0
        self.consistent_hash_ring = {}
        
        # Performance tracking
        self.decision_history: List[LoadBalancingDecision] = []
        self.performance_metrics = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "average_response_time": 0.0,
            "load_distribution_variance": 0.0
        }
        
        logger.info(f"Load balancer initialized with strategy: {strategy.value}")
    
    def register_agent(self, agent_id: str, capacity: int = 100):
        """Register a new agent with the load balancer"""
        try:
            self.agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                current_load=0,
                total_capacity=capacity,
                response_time=0.0,
                success_rate=1.0,
                last_heartbeat=datetime.now(),
                health_score=1.0,
                task_history=[]
            )
            
            # Add to consistent hash ring
            self._add_to_hash_ring(agent_id)
            
            logger.info(f"Agent {agent_id} registered with capacity {capacity}")
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the load balancer"""
        try:
            if agent_id in self.agent_metrics:
                del self.agent_metrics[agent_id]
                self._remove_from_hash_ring(agent_id)
                logger.info(f"Agent {agent_id} unregistered")
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
    
    def update_agent_metrics(self, agent_id: str, **kwargs):
        """Update agent metrics"""
        try:
            if agent_id in self.agent_metrics:
                agent = self.agent_metrics[agent_id]
                
                for key, value in kwargs.items():
                    if hasattr(agent, key):
                        setattr(agent, key, value)
                
                # Update health score
                agent.health_score = self._calculate_health_score(agent)
                
                logger.debug(f"Updated metrics for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to update metrics for agent {agent_id}: {e}")
    
    def select_agent(self, task_requirements: Dict[str, Any] = None) -> Optional[LoadBalancingDecision]:
        """Select the best agent using the configured strategy"""
        try:
            if not self.agent_metrics:
                logger.warning("No agents available for load balancing")
                return None
            
            # Filter healthy agents
            healthy_agents = self._get_healthy_agents()
            if not healthy_agents:
                logger.warning("No healthy agents available")
                return None
            
            # Apply load balancing strategy
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                selected_agent = self._round_robin_selection(healthy_agents)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                selected_agent = self._least_connections_selection(healthy_agents)
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                selected_agent = self._weighted_round_robin_selection(healthy_agents)
            elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                selected_agent = self._least_response_time_selection(healthy_agents)
            elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
                selected_agent = self._consistent_hash_selection(healthy_agents, task_requirements)
            elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
                selected_agent = self._adaptive_selection(healthy_agents, task_requirements)
            else:
                logger.error(f"Unknown load balancing strategy: {self.strategy}")
                return None
            
            if not selected_agent:
                logger.warning("No agent selected by load balancer")
                return None
            
            # Create decision record
            decision = LoadBalancingDecision(
                selected_agent_id=selected_agent.agent_id,
                strategy_used=self.strategy,
                reasoning=self._generate_reasoning(selected_agent),
                confidence_score=self._calculate_confidence(selected_agent),
                alternative_agents=self._get_alternative_agents(selected_agent.agent_id, healthy_agents)
            )
            
            # Update metrics
            self._update_decision_metrics(decision)
            
            # Increment agent load
            selected_agent.current_load += 1
            
            logger.info(f"Selected agent {selected_agent.agent_id} using {self.strategy.value}")
            return decision
            
        except Exception as e:
            logger.error(f"Failed to select agent: {e}")
            return None
    
    def _round_robin_selection(self, healthy_agents: List[AgentMetrics]) -> AgentMetrics:
        """Round-robin selection strategy"""
        if not healthy_agents:
            return None
        
        self.last_round_robin_index = (self.last_round_robin_index + 1) % len(healthy_agents)
        return healthy_agents[self.last_round_robin_index]
    
    def _least_connections_selection(self, healthy_agents: List[AgentMetrics]) -> AgentMetrics:
        """Least connections selection strategy"""
        if not healthy_agents:
            return None
        
        return min(healthy_agents, key=lambda x: x.current_load)
    
    def _weighted_round_robin_selection(self, healthy_agents: List[AgentMetrics]) -> AgentMetrics:
        """Weighted round-robin selection strategy"""
        if not healthy_agents:
            return None
        
        # Calculate weights based on capacity and health
        total_weight = sum(agent.total_capacity * agent.health_score for agent in healthy_agents)
        
        # Generate random value
        random_value = random.uniform(0, total_weight)
        
        # Find agent based on weight
        current_weight = 0
        for agent in healthy_agents:
            current_weight += agent.total_capacity * agent.health_score
            if random_value <= current_weight:
                return agent
        
        # Fallback to first agent
        return healthy_agents[0]
    
    def _least_response_time_selection(self, healthy_agents: List[AgentMetrics]) -> AgentMetrics:
        """Least response time selection strategy"""
        if not healthy_agents:
            return None
        
        return min(healthy_agents, key=lambda x: x.response_time)
    
    def _consistent_hash_selection(self, healthy_agents: List[AgentMetrics], 
                                 task_requirements: Dict[str, Any]) -> AgentMetrics:
        """Consistent hash selection strategy"""
        if not healthy_agents:
            return None
        
        # Generate hash key from task requirements
        if task_requirements:
            hash_key = hash(str(sorted(task_requirements.items())))
        else:
            hash_key = hash(str(time.time()))
        
        # Find agent in hash ring
        agent_id = self._get_agent_from_hash(hash_key)
        if agent_id and agent_id in self.agent_metrics:
            return self.agent_metrics[agent_id]
        
        # Fallback to first healthy agent
        return healthy_agents[0]
    
    def _adaptive_selection(self, healthy_agents: List[AgentMetrics], 
                          task_requirements: Dict[str, Any]) -> AgentMetrics:
        """Adaptive selection strategy that combines multiple factors"""
        if not healthy_agents:
            return None
        
        # Calculate scores for each agent
        agent_scores = []
        for agent in healthy_agents:
            score = self._calculate_agent_score(agent, task_requirements)
            agent_scores.append((agent, score))
        
        # Sort by score (highest first)
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top agent
        return agent_scores[0][0]
    
    def _calculate_agent_score(self, agent: AgentMetrics, 
                             task_requirements: Dict[str, Any]) -> float:
        """Calculate comprehensive score for agent selection"""
        try:
            # Base score starts at 100
            score = 100.0
            
            # Load factor (lower load = higher score)
            load_factor = 1.0 - (agent.current_load / agent.total_capacity)
            score += load_factor * 30
            
            # Health factor
            score += agent.health_score * 25
            
            # Response time factor (lower response time = higher score)
            if agent.response_time > 0:
                response_factor = max(0, 1.0 - (agent.response_time / 1000.0))  # Normalize to 1 second
                score += response_factor * 20
            
            # Success rate factor
            score += agent.success_rate * 15
            
            # Recent performance factor
            recent_performance = self._calculate_recent_performance(agent)
            score += recent_performance * 10
            
            return max(0, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate agent score: {e}")
            return 0.0
    
    def _calculate_recent_performance(self, agent: AgentMetrics) -> float:
        """Calculate recent performance score based on task history"""
        try:
            if not agent.task_history:
                return 0.5  # Neutral score for new agents
            
            # Look at last 10 tasks
            recent_tasks = agent.task_history[-10:]
            
            if not recent_tasks:
                return 0.5
            
            # Calculate success rate and average response time
            successful_tasks = sum(1 for task in recent_tasks if task.get("success", False))
            success_rate = successful_tasks / len(recent_tasks)
            
            response_times = [task.get("response_time", 0) for task in recent_tasks if task.get("response_time")]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                response_score = max(0, 1.0 - (avg_response_time / 1000.0))
            else:
                response_score = 0.5
            
            return (success_rate + response_score) / 2
            
        except Exception as e:
            logger.error(f"Failed to calculate recent performance: {e}")
            return 0.5
    
    def _get_healthy_agents(self) -> List[AgentMetrics]:
        """Get list of healthy agents"""
        try:
            current_time = datetime.now()
            healthy_agents = []
            
            for agent in self.agent_metrics.values():
                # Check if agent is healthy
                if (agent.health_score > 0.3 and 
                    current_time - agent.last_heartbeat < timedelta(minutes=5)):
                    healthy_agents.append(agent)
            
            return healthy_agents
            
        except Exception as e:
            logger.error(f"Failed to get healthy agents: {e}")
            return []
    
    def _calculate_health_score(self, agent: AgentMetrics) -> float:
        """Calculate agent health score"""
        try:
            # Base health score
            health_score = 1.0
            
            # Reduce score for high load
            if agent.current_load > agent.total_capacity * 0.8:
                health_score *= 0.7
            
            # Reduce score for poor success rate
            if agent.success_rate < 0.8:
                health_score *= agent.success_rate
            
            # Reduce score for slow response time
            if agent.response_time > 1000:  # > 1 second
                health_score *= 0.8
            
            # Reduce score for old heartbeat
            time_since_heartbeat = datetime.now() - agent.last_heartbeat
            if time_since_heartbeat > timedelta(minutes=2):
                health_score *= 0.5
            
            return max(0.0, min(1.0, health_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0.0
    
    def _add_to_hash_ring(self, agent_id: str):
        """Add agent to consistent hash ring"""
        try:
            # Generate hash for agent
            hash_value = hash(agent_id)
            self.consistent_hash_ring[hash_value] = agent_id
            
        except Exception as e:
            logger.error(f"Failed to add agent to hash ring: {e}")
    
    def _remove_from_hash_ring(self, agent_id: str):
        """Remove agent from consistent hash ring"""
        try:
            # Find and remove hash entry
            hash_value = hash(agent_id)
            if hash_value in self.consistent_hash_ring:
                del self.consistent_hash_ring[hash_value]
                
        except Exception as e:
            logger.error(f"Failed to remove agent from hash ring: {e}")
    
    def _get_agent_from_hash(self, hash_key: int) -> Optional[str]:
        """Get agent from hash ring using consistent hashing"""
        try:
            if not self.consistent_hash_ring:
                return None
            
            # Find the next hash value in the ring
            hash_values = sorted(self.consistent_hash_ring.keys())
            
            for hash_value in hash_values:
                if hash_value >= hash_key:
                    return self.consistent_hash_ring[hash_value]
            
            # Wrap around to first hash value
            return self.consistent_hash_ring[hash_values[0]]
            
        except Exception as e:
            logger.error(f"Failed to get agent from hash ring: {e}")
            return None
    
    def _generate_reasoning(self, agent: AgentMetrics) -> str:
        """Generate human-readable reasoning for agent selection"""
        try:
            reasons = []
            
            if agent.current_load < agent.total_capacity * 0.3:
                reasons.append("low load")
            
            if agent.health_score > 0.8:
                reasons.append("excellent health")
            
            if agent.response_time < 100:
                reasons.append("fast response time")
            
            if agent.success_rate > 0.95:
                reasons.append("high success rate")
            
            if not reasons:
                reasons.append("best available option")
            
            return f"Selected due to: {', '.join(reasons)}"
            
        except Exception as e:
            logger.error(f"Failed to generate reasoning: {e}")
            return "Selected based on load balancing algorithm"
    
    def _calculate_confidence(self, agent: AgentMetrics) -> float:
        """Calculate confidence score for the selection"""
        try:
            # Base confidence
            confidence = 0.5
            
            # Increase confidence for healthy agents
            confidence += agent.health_score * 0.3
            
            # Increase confidence for agents with low load
            load_factor = 1.0 - (agent.current_load / agent.total_capacity)
            confidence += load_factor * 0.2
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Failed to calculate confidence: {e}")
            return 0.5
    
    def _get_alternative_agents(self, selected_agent_id: str, 
                               healthy_agents: List[AgentMetrics]) -> List[str]:
        """Get list of alternative agent IDs"""
        try:
            alternatives = []
            for agent in healthy_agents:
                if agent.agent_id != selected_agent_id:
                    alternatives.append(agent.agent_id)
            
            return alternatives[:3]  # Return top 3 alternatives
            
        except Exception as e:
            logger.error(f"Failed to get alternative agents: {e}")
            return []
    
    def _update_decision_metrics(self, decision: LoadBalancingDecision):
        """Update performance metrics after decision"""
        try:
            self.performance_metrics["total_decisions"] += 1
            
            # Track decision in history
            self.decision_history.append(decision)
            
            # Keep only last 1000 decisions
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-1000:]
            
            logger.debug(f"Updated decision metrics for agent {decision.selected_agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to update decision metrics: {e}")
    
    def change_strategy(self, new_strategy: LoadBalancingStrategy):
        """Change the load balancing strategy"""
        try:
            old_strategy = self.strategy
            self.strategy = new_strategy
            
            logger.info(f"Load balancing strategy changed from {old_strategy.value} to {new_strategy.value}")
            
        except Exception as e:
            logger.error(f"Failed to change load balancing strategy: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get load balancer system status"""
        try:
            return {
                "strategy": self.strategy.value,
                "total_agents": len(self.agent_metrics),
                "healthy_agents": len(self._get_healthy_agents()),
                "performance_metrics": self.performance_metrics,
                "agent_metrics": {
                    agent_id: {
                        "current_load": agent.current_load,
                        "total_capacity": agent.total_capacity,
                        "health_score": agent.health_score,
                        "response_time": agent.response_time,
                        "success_rate": agent.success_rate
                    }
                    for agent_id, agent in self.agent_metrics.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}


# Global load balancer instance
load_balancer = LoadBalancer()

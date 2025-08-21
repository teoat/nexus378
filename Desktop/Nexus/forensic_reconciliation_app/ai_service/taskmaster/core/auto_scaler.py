"""
Auto Scaler - Automatic Scaling Engine

This module implements the AutoScaler class that handles automatic scaling
of agents and resources based on workload and performance metrics.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import math

from ..models.agent import Agent, AgentStatus, AgentType
from ..models.job import Job, JobStatus, JobPriority, JobType


class ScalingPolicy(Enum):
    """Scaling policy types."""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"
    SCHEDULED = "scheduled"


class ScalingAction(Enum):
    """Scaling action types."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    EMERGENCY_SCALE = "emergency_scale"


class ScalingTrigger(Enum):
    """Scaling trigger types."""
    CPU_THRESHOLD = "cpu_threshold"
    MEMORY_THRESHOLD = "memory_threshold"
    QUEUE_LENGTH = "queue_length"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    SCHEDULED = "scheduled"
    MANUAL = "manual"


@dataclass
class ScalingMetrics:
    """Scaling performance metrics."""
    
    total_scaling_events: int = 0
    scale_up_events: int = 0
    scale_down_events: int = 0
    average_scaling_time: float = 0.0
    scaling_accuracy: float = 0.0
    resource_efficiency: float = 0.0
    cost_savings: float = 0.0
    
    def update_average_scaling_time(self, new_time: float):
        """Update average scaling time."""
        self.average_scaling_time = (
            (self.average_scaling_time * self.total_scaling_events + new_time) /
            (self.total_scaling_events + 1)
        )


@dataclass
class ScalingDecision:
    """Scaling decision data."""
    
    action: ScalingAction
    target_count: int
    reason: str
    trigger: ScalingTrigger
    confidence: float
    estimated_impact: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class ScalingRule:
    """Scaling rule definition."""
    
    id: str
    name: str
    trigger: ScalingTrigger
    threshold: float
    action: ScalingAction
    target_count: int
    cooldown: timedelta
    enabled: bool = True
    priority: int = 1
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


class AutoScaler:
    """
    Automatic scaling engine for the Taskmaster system.
    
    The AutoScaler is responsible for:
    - Monitoring system workload and performance
    - Making intelligent scaling decisions
    - Implementing various scaling policies
    - Managing scaling rules and thresholds
    - Optimizing resource utilization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the AutoScaler."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Scaling configuration
        self.policy = ScalingPolicy(config.get('scaling_policy', 'hybrid'))
        self.min_agents = config.get('min_agents', 5)
        self.max_agents = config.get('max_agents', 100)
        self.scale_up_threshold = config.get('scale_up_threshold', 0.8)
        self.scale_down_threshold = config.get('scale_down_threshold', 0.2)
        self.scaling_cooldown = timedelta(minutes=config.get('scaling_cooldown_minutes', 5))
        self.emergency_threshold = config.get('emergency_threshold', 0.95)
        
        # Scaling rules
        self.scaling_rules: Dict[str, ScalingRule] = {}
        self.active_rules: Dict[str, ScalingRule] = {}
        
        # Scaling metrics
        self.metrics = ScalingMetrics()
        
        # Internal state
        self.last_scaling_event: Optional[datetime] = None
        self.scaling_history: List[ScalingDecision] = []
        self.workload_metrics: deque = deque(maxlen=1000)
        self.performance_metrics: deque = deque(maxlen=1000)
        
        # Scaling policies
        self.reactive_scaling = config.get('reactive_scaling', True)
        self.predictive_scaling = config.get('predictive_scaling', True)
        self.scheduled_scaling = config.get('scheduled_scaling', True)
        
        # Event loop
        self.loop = asyncio.get_event_loop()
        
        self.logger.info(f"AutoScaler initialized with policy: {self.policy}")
    
    async def start(self):
        """Start the AutoScaler."""
        self.logger.info("Starting AutoScaler...")
        
        # Initialize scaling rules
        await self._initialize_scaling_rules()
        
        # Start background tasks
        asyncio.create_task(self._monitor_workload())
        asyncio.create_task(self._evaluate_scaling_needs())
        asyncio.create_task(self._execute_scaling_actions())
        asyncio.create_task(self._update_scaling_metrics())
        asyncio.create_task(self._cleanup_scaling_history())
        
        self.logger.info("AutoScaler started successfully")
    
    async def stop(self):
        """Stop the AutoScaler."""
        self.logger.info("Stopping AutoScaler...")
        self.logger.info("AutoScaler stopped")
    
    async def add_scaling_rule(self, rule: ScalingRule):
        """Add a new scaling rule."""
        self.scaling_rules[rule.id] = rule
        if rule.enabled:
            self.active_rules[rule.id] = rule
        self.logger.info(f"Added scaling rule: {rule.name}")
    
    async def remove_scaling_rule(self, rule_id: str):
        """Remove a scaling rule."""
        if rule_id in self.scaling_rules:
            del self.scaling_rules[rule_id]
            if rule_id in self.active_rules:
                del self.active_rules[rule_id]
            self.logger.info(f"Removed scaling rule: {rule_id}")
    
    async def enable_scaling_rule(self, rule_id: str):
        """Enable a scaling rule."""
        if rule_id in self.scaling_rules:
            rule = self.scaling_rules[rule_id]
            rule.enabled = True
            self.active_rules[rule_id] = rule
            self.logger.info(f"Enabled scaling rule: {rule_id}")
    
    async def disable_scaling_rule(self, rule_id: str):
        """Disable a scaling rule."""
        if rule_id in self.active_rules:
            del self.active_rules[rule_id]
            self.scaling_rules[rule_id].enabled = False
            self.logger.info(f"Disabled scaling rule: {rule_id}")
    
    async def get_scaling_metrics(self) -> ScalingMetrics:
        """Get current scaling performance metrics."""
        return self.metrics
    
    async def get_scaling_history(self, duration: timedelta = timedelta(hours=24)) -> List[ScalingDecision]:
        """Get scaling history for a specific duration."""
        cutoff_time = datetime.utcnow() - duration
        return [
            decision for decision in self.scaling_history
            if decision.timestamp >= cutoff_time
        ]
    
    async def manual_scale(self, target_count: int, reason: str = "Manual scaling"):
        """Trigger manual scaling."""
        try:
            # Validate target count
            if target_count < self.min_agents or target_count > self.max_agents:
                raise ValueError(f"Target count {target_count} is outside allowed range [{self.min_agents}, {self.max_agents}]")
            
            # Create scaling decision
            current_count = await self._get_current_agent_count()
            if target_count > current_count:
                action = ScalingAction.SCALE_UP
            elif target_count < current_count:
                action = ScalingAction.SCALE_DOWN
            else:
                action = ScalingAction.MAINTAIN
            
            decision = ScalingDecision(
                action=action,
                target_count=target_count,
                reason=reason,
                trigger=ScalingTrigger.MANUAL,
                confidence=1.0,
                estimated_impact={
                    'current_count': current_count,
                    'change': target_count - current_count,
                    'estimated_time': self._estimate_scaling_time(abs(target_count - current_count))
                },
                timestamp=datetime.utcnow()
            )
            
            # Execute scaling
            await self._execute_scaling_decision(decision)
            
            self.logger.info(f"Manual scaling executed: {action.value} to {target_count} agents")
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in manual scaling: {e}")
            raise
    
    async def _monitor_workload(self):
        """Monitor system workload and performance."""
        while True:
            try:
                # Collect workload metrics
                workload_metrics = await self._collect_workload_metrics()
                self.workload_metrics.append(workload_metrics)
                
                # Collect performance metrics
                performance_metrics = await self._collect_performance_metrics()
                self.performance_metrics.append(performance_metrics)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring workload: {e}")
                await asyncio.sleep(30)
    
    async def _evaluate_scaling_needs(self):
        """Evaluate if scaling is needed."""
        while True:
            try:
                # Check if we're in cooldown period
                if (self.last_scaling_event and 
                    datetime.utcnow() - self.last_scaling_event < self.scaling_cooldown):
                    await asyncio.sleep(10)
                    continue
                
                # Evaluate based on policy
                if self.policy == ScalingPolicy.REACTIVE:
                    decision = await self._evaluate_reactive_scaling()
                elif self.policy == ScalingPolicy.PREDICTIVE:
                    decision = await self._evaluate_predictive_scaling()
                elif self.policy == ScalingPolicy.HYBRID:
                    decision = await self._evaluate_hybrid_scaling()
                elif self.policy == ScalingPolicy.SCHEDULED:
                    decision = await self._evaluate_scheduled_scaling()
                else:
                    decision = None
                
                # Execute scaling decision if needed
                if decision and decision.action != ScalingAction.MAINTAIN:
                    await self._execute_scaling_decision(decision)
                
                await asyncio.sleep(60)  # Evaluate every minute
                
            except Exception as e:
                self.logger.error(f"Error evaluating scaling needs: {e}")
                await asyncio.sleep(60)
    
    async def _evaluate_reactive_scaling(self) -> Optional[ScalingDecision]:
        """Evaluate scaling needs using reactive approach."""
        try:
            if not self.workload_metrics:
                return None
            
            # Get latest metrics
            latest_metrics = self.workload_metrics[-1]
            current_count = await self._get_current_agent_count()
            
            # Calculate current utilization
            cpu_utilization = latest_metrics.get('cpu_utilization', 0.0)
            memory_utilization = latest_metrics.get('memory_utilization', 0.0)
            queue_length = latest_metrics.get('queue_length', 0)
            response_time = latest_metrics.get('response_time', 0.0)
            
            # Determine scaling action
            action = ScalingAction.MAINTAIN
            target_count = current_count
            reason = "No scaling needed"
            confidence = 0.0
            
            # Check for scale up conditions
            if (cpu_utilization > self.scale_up_threshold or 
                memory_utilization > self.scale_up_threshold or
                queue_length > current_count * 2 or
                response_time > self.config.get('max_response_time', 5.0)):
                
                action = ScalingAction.SCALE_UP
                target_count = min(current_count + self._calculate_scale_up_amount(latest_metrics), self.max_agents)
                reason = f"High utilization: CPU={cpu_utilization:.1%}, Memory={memory_utilization:.1%}, Queue={queue_length}"
                confidence = min(0.9, (cpu_utilization + memory_utilization) / 2)
            
            # Check for scale down conditions
            elif (cpu_utilization < self.scale_down_threshold and 
                  memory_utilization < self.scale_down_threshold and
                  queue_length < current_count * 0.5 and
                  response_time < self.config.get('min_response_time', 1.0)):
                
                action = ScalingAction.SCALE_DOWN
                target_count = max(current_count - self._calculate_scale_down_amount(latest_metrics), self.min_agents)
                reason = f"Low utilization: CPU={cpu_utilization:.1%}, Memory={memory_utilization:.1%}, Queue={queue_length}"
                confidence = min(0.9, (1 - cpu_utilization + 1 - memory_utilization) / 2)
            
            # Check for emergency scaling
            if (cpu_utilization > self.emergency_threshold or 
                memory_utilization > self.emergency_threshold):
                action = ScalingAction.EMERGENCY_SCALE
                target_count = min(current_count + max(5, current_count // 2), self.max_agents)
                reason = f"Emergency scaling: CPU={cpu_utilization:.1%}, Memory={memory_utilization:.1%}"
                confidence = 1.0
            
            if action != ScalingAction.MAINTAIN:
                return ScalingDecision(
                    action=action,
                    target_count=target_count,
                    reason=reason,
                    trigger=ScalingTrigger.CPU_THRESHOLD,
                    confidence=confidence,
                    estimated_impact={
                        'current_count': current_count,
                        'change': target_count - current_count,
                        'estimated_time': self._estimate_scaling_time(abs(target_count - current_count))
                    },
                    timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in reactive scaling evaluation: {e}")
            return None
    
    async def _evaluate_predictive_scaling(self) -> Optional[ScalingDecision]:
        """Evaluate scaling needs using predictive approach."""
        try:
            if len(self.workload_metrics) < 10:
                return None
            
            # Analyze workload trends
            trend_analysis = self._analyze_workload_trends()
            
            if not trend_analysis:
                return None
            
            current_count = await self._get_current_agent_count()
            predicted_workload = trend_analysis.get('predicted_workload', 0.0)
            trend_direction = trend_analysis.get('trend_direction', 'stable')
            confidence = trend_analysis.get('confidence', 0.0)
            
            # Make predictive scaling decision
            if trend_direction == 'increasing' and confidence > 0.7:
                target_count = min(current_count + 2, self.max_agents)
                return ScalingDecision(
                    action=ScalingAction.SCALE_UP,
                    target_count=target_count,
                    reason=f"Predictive scaling: workload trend is {trend_direction}",
                    trigger=ScalingTrigger.SCHEDULED,
                    confidence=confidence,
                    estimated_impact={
                        'current_count': current_count,
                        'change': 2,
                        'estimated_time': self._estimate_scaling_time(2)
                    },
                    timestamp=datetime.utcnow()
                )
            
            elif trend_direction == 'decreasing' and confidence > 0.7:
                target_count = max(current_count - 1, self.min_agents)
                return ScalingDecision(
                    action=ScalingAction.SCALE_DOWN,
                    target_count=target_count,
                    reason=f"Predictive scaling: workload trend is {trend_direction}",
                    trigger=ScalingTrigger.SCHEDULED,
                    confidence=confidence,
                    estimated_impact={
                        'current_count': current_count,
                        'change': -1,
                        'estimated_time': self._estimate_scaling_time(1)
                    },
                    timestamp=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in predictive scaling evaluation: {e}")
            return None
    
    async def _evaluate_hybrid_scaling(self) -> Optional[ScalingDecision]:
        """Evaluate scaling needs using hybrid approach."""
        try:
            # Combine reactive and predictive approaches
            reactive_decision = await self._evaluate_reactive_scaling()
            predictive_decision = await self._evaluate_predictive_scaling()
            
            if not reactive_decision and not predictive_decision:
                return None
            
            # Prioritize reactive decisions over predictive ones
            if reactive_decision:
                return reactive_decision
            
            # Use predictive decision if confidence is high enough
            if predictive_decision and predictive_decision.confidence > 0.8:
                return predictive_decision
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in hybrid scaling evaluation: {e}")
            return None
    
    async def _evaluate_scheduled_scaling(self) -> Optional[ScalingDecision]:
        """Evaluate scaling needs using scheduled approach."""
        try:
            current_time = datetime.utcnow()
            current_hour = current_time.hour
            
            # Define scheduled scaling rules
            scheduled_rules = {
                8: {'action': ScalingAction.SCALE_UP, 'count': 3, 'reason': 'Morning workload increase'},
                12: {'action': ScalingAction.SCALE_UP, 'count': 2, 'reason': 'Lunch hour workload'},
                18: {'action': ScalingAction.SCALE_DOWN, 'count': 2, 'reason': 'Evening workload decrease'},
                22: {'action': ScalingAction.SCALE_DOWN, 'count': 3, 'reason': 'Night workload decrease'}
            }
            
            if current_hour in scheduled_rules:
                rule = scheduled_rules[current_hour]
                current_count = await self._get_current_agent_count()
                
                if rule['action'] == ScalingAction.SCALE_UP:
                    target_count = min(current_count + rule['count'], self.max_agents)
                else:
                    target_count = max(current_count - rule['count'], self.min_agents)
                
                return ScalingDecision(
                    action=rule['action'],
                    target_count=target_count,
                    reason=rule['reason'],
                    trigger=ScalingTrigger.SCHEDULED,
                    confidence=0.9,
                    estimated_impact={
                        'current_count': current_count,
                        'change': target_count - current_count,
                        'estimated_time': self._estimate_scaling_time(abs(target_count - current_count))
                    },
                    timestamp=current_time
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in scheduled scaling evaluation: {e}")
            return None
    
    async def _execute_scaling_decision(self, decision: ScalingDecision):
        """Execute a scaling decision."""
        try:
            start_time = datetime.utcnow()
            
            self.logger.info(f"Executing scaling decision: {decision.action.value} to {decision.target_count} agents")
            
            # Update metrics
            self.metrics.total_scaling_events += 1
            if decision.action == ScalingAction.SCALE_UP:
                self.metrics.scale_up_events += 1
            elif decision.action == ScalingAction.SCALE_DOWN:
                self.metrics.scale_down_events += 1
            
            # Execute scaling action
            if decision.action == ScalingAction.SCALE_UP:
                await self._scale_up_agents(decision.target_count)
            elif decision.action == ScalingAction.SCALE_DOWN:
                await self._scale_down_agents(decision.target_count)
            
            # Update scaling history
            self.scaling_history.append(decision)
            
            # Update last scaling event time
            self.last_scaling_event = datetime.utcnow()
            
            # Update metrics
            scaling_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.update_average_scaling_time(scaling_time)
            
            self.logger.info(f"Scaling decision executed successfully in {scaling_time:.2f} seconds")
            
        except Exception as e:
            self.logger.error(f"Error executing scaling decision: {e}")
    
    async def _scale_up_agents(self, target_count: int):
        """Scale up the number of agents."""
        current_count = await self._get_current_agent_count()
        needed = target_count - current_count
        
        if needed <= 0:
            return
        
        self.logger.info(f"Scaling up {needed} agents")
        
        # This would integrate with your agent management system
        # For now, simulate agent creation
        for i in range(needed):
            agent_id = f"agent_{current_count + i + 1}"
            await self._create_agent(agent_id)
    
    async def _scale_down_agents(self, target_count: int):
        """Scale down the number of agents."""
        current_count = await self._get_current_agent_count()
        to_remove = current_count - target_count
        
        if to_remove <= 0:
            return
        
        self.logger.info(f"Scaling down {to_remove} agents")
        
        # This would integrate with your agent management system
        # For now, simulate agent removal
        for i in range(to_remove):
            agent_id = f"agent_{current_count - i}"
            await self._remove_agent(agent_id)
    
    async def _create_agent(self, agent_id: str):
        """Create a new agent."""
        # This would integrate with your agent management system
        self.logger.info(f"Creating agent: {agent_id}")
        await asyncio.sleep(1)  # Simulate creation time
    
    async def _remove_agent(self, agent_id: str):
        """Remove an existing agent."""
        # This would integrate with your agent management system
        self.logger.info(f"Removing agent: {agent_id}")
        await asyncio.sleep(1)  # Simulate removal time
    
    async def _collect_workload_metrics(self) -> Dict[str, Any]:
        """Collect current workload metrics."""
        try:
            # This would integrate with your monitoring system
            # For now, simulate metrics collection
            
            import random
            
            return {
                'cpu_utilization': random.uniform(0.1, 0.9),
                'memory_utilization': random.uniform(0.1, 0.9),
                'queue_length': random.randint(0, 50),
                'response_time': random.uniform(0.5, 5.0),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting workload metrics: {e}")
            return {}
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics."""
        try:
            # This would integrate with your monitoring system
            # For now, simulate metrics collection
            
            import random
            
            return {
                'throughput': random.uniform(100, 1000),
                'error_rate': random.uniform(0.0, 0.05),
                'availability': random.uniform(0.95, 1.0),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")
            return {}
    
    async def _get_current_agent_count(self) -> int:
        """Get current number of active agents."""
        # This would integrate with your agent management system
        # For now, return a simulated count
        return 10
    
    def _calculate_scale_up_amount(self, metrics: Dict[str, Any]) -> int:
        """Calculate how many agents to add."""
        cpu_utilization = metrics.get('cpu_utilization', 0.0)
        memory_utilization = metrics.get('memory_utilization', 0.0)
        queue_length = metrics.get('queue_length', 0)
        
        # Base scaling amount
        base_amount = 2
        
        # Adjust based on utilization
        if max(cpu_utilization, memory_utilization) > 0.9:
            base_amount = 5
        elif max(cpu_utilization, memory_utilization) > 0.8:
            base_amount = 3
        
        # Adjust based on queue length
        if queue_length > 20:
            base_amount += 2
        
        return min(base_amount, 10)  # Cap at 10 agents per scaling event
    
    def _calculate_scale_down_amount(self, metrics: Dict[str, Any]) -> int:
        """Calculate how many agents to remove."""
        cpu_utilization = metrics.get('cpu_utilization', 0.0)
        memory_utilization = metrics.get('memory_utilization', 0.0)
        queue_length = metrics.get('queue_length', 0)
        
        # Conservative scale down
        if max(cpu_utilization, memory_utilization) < 0.3 and queue_length < 5:
            return 2
        elif max(cpu_utilization, memory_utilization) < 0.2 and queue_length < 2:
            return 3
        
        return 1
    
    def _estimate_scaling_time(self, agent_count: int) -> float:
        """Estimate time required for scaling operation."""
        # Base scaling time per agent
        base_time_per_agent = 30.0  # seconds
        
        # Add overhead for coordination
        overhead = 10.0  # seconds
        
        return (agent_count * base_time_per_agent) + overhead
    
    def _analyze_workload_trends(self) -> Optional[Dict[str, Any]]:
        """Analyze workload trends for predictive scaling."""
        try:
            if len(self.workload_metrics) < 10:
                return None
            
            # Simple trend analysis using linear regression
            # In a real system, you'd use more sophisticated ML models
            
            recent_metrics = list(self.workload_metrics)[-10:]
            cpu_values = [m.get('cpu_utilization', 0.0) for m in recent_metrics]
            
            # Calculate trend
            n = len(cpu_values)
            x_sum = sum(range(n))
            y_sum = sum(cpu_values)
            xy_sum = sum(i * val for i, val in enumerate(cpu_values))
            x2_sum = sum(i * i for i in range(n))
            
            if n * x2_sum - x_sum * x_sum == 0:
                return None
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
            
            # Determine trend direction
            if slope > 0.01:
                trend_direction = 'increasing'
            elif slope < -0.01:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
            
            # Calculate confidence based on slope magnitude
            confidence = min(0.9, abs(slope) * 10)
            
            # Predict future workload
            predicted_workload = cpu_values[-1] + slope * 5  # 5 time steps ahead
            
            return {
                'trend_direction': trend_direction,
                'slope': slope,
                'confidence': confidence,
                'predicted_workload': predicted_workload
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing workload trends: {e}")
            return None
    
    async def _execute_scaling_actions(self):
        """Execute pending scaling actions."""
        # This would handle the actual execution of scaling actions
        # For now, it's handled in the main evaluation loop
        pass
    
    async def _update_scaling_metrics(self):
        """Update scaling performance metrics."""
        while True:
            try:
                # Calculate scaling accuracy
                if self.metrics.total_scaling_events > 0:
                    successful_scales = self.metrics.scale_up_events + self.metrics.scale_down_events
                    self.metrics.scaling_accuracy = successful_scales / self.metrics.total_scaling_events
                
                # Calculate resource efficiency
                # This would be based on actual resource utilization after scaling
                self.metrics.resource_efficiency = 0.8  # Placeholder
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating scaling metrics: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_scaling_history(self):
        """Clean up old scaling history records."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=7)
                
                # Remove old records
                self.scaling_history = [
                    decision for decision in self.scaling_history
                    if decision.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error cleaning up scaling history: {e}")
                await asyncio.sleep(3600)
    
    async def _initialize_scaling_rules(self):
        """Initialize default scaling rules."""
        default_rules = [
            ScalingRule(
                name="High CPU Utilization",
                trigger=ScalingTrigger.CPU_THRESHOLD,
                threshold=0.8,
                action=ScalingAction.SCALE_UP,
                target_count=5,
                cooldown=timedelta(minutes=5)
            ),
            ScalingRule(
                name="High Memory Utilization",
                trigger=ScalingTrigger.MEMORY_THRESHOLD,
                threshold=0.8,
                action=ScalingAction.SCALE_UP,
                target_count=3,
                cooldown=timedelta(minutes=5)
            ),
            ScalingRule(
                name="Long Queue",
                trigger=ScalingTrigger.QUEUE_LENGTH,
                threshold=20,
                action=ScalingAction.SCALE_UP,
                target_count=2,
                cooldown=timedelta(minutes=3)
            ),
            ScalingRule(
                name="Low Utilization",
                trigger=ScalingTrigger.CPU_THRESHOLD,
                threshold=0.2,
                action=ScalingAction.SCALE_DOWN,
                target_count=1,
                cooldown=timedelta(minutes=10)
            )
        ]
        
        for rule in default_rules:
            await self.add_scaling_rule(rule)


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        'scaling_policy': 'hybrid',
        'min_agents': 5,
        'max_agents': 100,
        'scale_up_threshold': 0.8,
        'scale_down_threshold': 0.2,
        'scaling_cooldown_minutes': 5,
        'emergency_threshold': 0.95,
        'reactive_scaling': True,
        'predictive_scaling': True,
        'scheduled_scaling': True,
        'max_response_time': 5.0,
        'min_response_time': 1.0
    }
    
    # Initialize auto scaler
    scaler = AutoScaler(config)
    
    print("AutoScaler system initialized successfully!")

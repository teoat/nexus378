"""
AutoScaler for the Taskmaster System
Provides logic for automatically scaling the number of agents based on workload.
"""

import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ScalingDecision:
    """Enum-like class for scaling decisions."""
    SCALE_UP = "SCALE_UP"
    SCALE_DOWN = "SCALE_DOWN"
    HOLD = "HOLD"

class AutoScaler:
    """
    AutoScaler class to manage the scaling of AI agents.
    """
    def __init__(self, mcp_server, config: Dict[str, Any]):
        """
        Initializes the AutoScaler.

        Args:
            mcp_server: An instance of the MCPServer to get metrics from.
            config: A dictionary containing scaling configuration.
                Expected keys:
                - MIN_AGENTS: Minimum number of agents to maintain.
                - MAX_AGENTS: Maximum number of agents to scale up to.
                - TASKS_PER_AGENT_THRESHOLD: Number of pending tasks per agent that triggers a scale up.
                - IDLE_AGENT_PERCENT_THRESHOLD: Percentage of idle agents that triggers a scale down.
                - COOLDOWN_PERIOD_S: Seconds to wait between scaling actions.
        """
        self.mcp_server = mcp_server
        self.min_agents = config.get("MIN_AGENTS", 1)
        self.max_agents = config.get("MAX_AGENTS", 10)
        self.tasks_per_agent_threshold = config.get("TASKS_PER_AGENT_THRESHOLD", 10)
        self.idle_agent_percent_threshold = config.get("IDLE_AGENT_PERCENT_THRESHOLD", 0.5) # 50%
        self.cooldown_period_s = config.get("COOLDOWN_PERIOD_S", 60) # 60 seconds

        self.last_scaling_time = 0
        logger.info(f"AutoScaler initialized with config: {config}")

    def make_scaling_decision(self) -> str:
        """
        Analyzes system metrics and decides whether to scale up, down, or hold.

        Returns:
            A string indicating the scaling decision ('SCALE_UP', 'SCALE_DOWN', 'HOLD').
        """
        # Check if we are in a cooldown period
        if time.time() - self.last_scaling_time < self.cooldown_period_s:
            return ScalingDecision.HOLD

        # Get current metrics from the MCPServer
        system_status = self.mcp_server.get_system_status()
        pending_tasks = system_status.get("task_status", {}).get("pending", 0)
        total_agents = system_status.get("agents", {}).get("total_registered", 0)
        in_progress_tasks = system_status.get("task_status", {}).get("in_progress", 0)

        # In a real system, we'd have a more direct way to count idle agents.
        # Here we estimate busy agents by the number of in-progress tasks.
        # This assumes one task per agent, which is a simplification.
        busy_agents = in_progress_tasks
        idle_agents = total_agents - busy_agents

        logger.debug(f"AutoScaler metrics: Pending Tasks={pending_tasks}, Total Agents={total_agents}, Busy Agents={busy_agents}")

        # --- Scale Up Logic ---
        # If there are pending tasks and the number of tasks per agent exceeds the threshold
        # and we are below the max agent limit.
        if total_agents > 0 and (pending_tasks / total_agents) > self.tasks_per_agent_threshold:
            if total_agents < self.max_agents:
                logger.info("Decision: SCALE_UP. High task load per agent.")
                self.last_scaling_time = time.time()
                return ScalingDecision.SCALE_UP

        # --- Scale Down Logic ---
        # If there are no pending tasks and a significant percentage of agents are idle
        # and we are above the min agent limit.
        if pending_tasks == 0 and total_agents > 0:
            idle_percentage = idle_agents / total_agents
            if idle_percentage >= self.idle_agent_percent_threshold:
                if total_agents > self.min_agents:
                    logger.info("Decision: SCALE_DOWN. High percentage of idle agents.")
                    self.last_scaling_time = time.time()
                    return ScalingDecision.SCALE_DOWN

        # --- Hold Logic ---
        # If none of the above conditions are met, maintain the current number of agents.
        logger.debug("Decision: HOLD. System is stable.")
        return ScalingDecision.HOLD

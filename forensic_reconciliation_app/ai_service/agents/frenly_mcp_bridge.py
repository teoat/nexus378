"""
Frenly MCP Bridge - Connects Frenly's high-level commands to specialized sub-agents

This bridge translates Frenly's app management commands into specific agent actions
and coordinates the execution of specialized AI agents.
"""

from typing import Dict, List, Any, Optional
from .frenly_meta_agent import AppContext, AppCommand, AppResponse, ModeIntersection
import logging

logger = logging.getLogger(__name__)


class FrenlyMCPBridge:
    """
    Bridge between Frenly's high-level commands and specialized sub-agent execution.
    
    This class handles the translation of Frenly's app management commands into
    specific actions that specialized agents can execute.
    """
    
    def __init__(self, frenly_agent):
        """
        Initialize the MCP bridge.
        
        Args:
            frenly_agent: The FrenlyMetaAgent instance to bridge with
        """
        self.frenly_agent = frenly_agent
        self.agent_registry: Dict[str, Any] = {}
        self.workflow_registry: Dict[str, List[str]] = {}
        
        logger.info("Frenly MCP Bridge initialized")
    
    def register_agent(self, agent_name: str, agent_instance: Any):
        """
        Register a specialized agent with the bridge.
        
        Args:
            agent_name: Name of the agent
            agent_instance: The agent instance
        """
        self.agent_registry[agent_name] = agent_instance
        logger.info(f"Registered agent: {agent_name}")
    
    def register_workflow(self, workflow_name: str, agent_sequence: List[str]):
        """
        Register a workflow sequence with the bridge.
        
        Args:
            workflow_name: Name of the workflow
            agent_sequence: Sequence of agent names to execute
        """
        self.workflow_registry[workflow_name] = agent_sequence
        logger.info(f"Registered workflow: {workflow_name} -> {agent_sequence}")
    
    def execute_command(self, command: AppCommand) -> AppResponse:
        """
        Execute a command through the appropriate agents.
        
        Args:
            command: The command to execute
            
        Returns:
            AppResponse with execution results
        """
        try:
            # Get current mode intersection to determine agent priorities
            current_intersection = self.frenly_agent._get_current_mode_intersection()
            
            if not current_intersection:
                return AppResponse(
                    success=False,
                    message="No mode intersection found for current configuration"
                )
            
            # Select appropriate agents based on mode intersection
            selected_agents = self._select_agents_for_command(command, current_intersection)
            
            # Execute through selected agents
            results = self._execute_through_agents(command, selected_agents)
            
            # Synthesize results
            synthesized_response = self._synthesize_agent_results(results, current_intersection)
            
            return synthesized_response
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return AppResponse(
                success=False,
                message=f"Command execution error: {str(e)}"
            )
    
    def _select_agents_for_command(self, command: AppCommand, intersection: ModeIntersection) -> List[str]:
        """
        Select appropriate agents based on the command and current mode intersection.
        
        Args:
            command: The command to execute
            intersection: Current mode intersection
            
        Returns:
            List of agent names to execute
        """
        # Start with the intersection's agent priorities
        selected_agents = intersection.agent_priorities.copy()
        
        # Filter based on command type
        if command.command_type == "switch_app_mode":
            # For mode switching, we need reconciliation and fraud agents
            selected_agents = [agent for agent in selected_agents if "reconciliation" in agent or "fraud" in agent]
        elif command.command_type == "change_thinking_perspective":
            # For perspective changes, we need evidence and litigation agents
            selected_agents = [agent for agent in selected_agents if "evidence" in agent or "litigation" in agent]
        elif command.command_type == "change_ai_mode":
            # For AI mode changes, we need all agents
            pass  # Keep all agents
        elif command.command_type == "change_dashboard_view":
            # For view changes, we need view-specific agents
            selected_agents = self._get_view_specific_agents(command.target_view, selected_agents)
        
        return selected_agents
    
    def _get_view_specific_agents(self, target_view: str, available_agents: List[str]) -> List[str]:
        """
        Get agents specific to a particular dashboard view.
        
        Args:
            target_view: The target dashboard view
            available_agents: List of available agents
            
        Returns:
            List of view-specific agents
        """
        view_agent_mapping = {
            "reconciliation": ["reconciliation_agent"],
            "fraud_analysis": ["fraud_agent"],
            "evidence_viewer": ["evidence_agent"],
            "entity_network": ["entity_agent"],
            "legal_analysis": ["litigation_agent"],
            "construction_projects": ["reconciliation_agent", "fraud_agent"],
            "financial_statements": ["reconciliation_agent", "fraud_agent"],
            "audit_trails": ["reconciliation_agent", "fraud_agent"],
            "risk_assessment": ["risk_agent"],
            "compliance_reports": ["litigation_agent", "reconciliation_agent"]
        }
        
        view_agents = view_agent_mapping.get(target_view, [])
        return [agent for agent in available_agents if agent in view_agents]
    
    def _execute_through_agents(self, command: AppCommand, selected_agents: List[str]) -> Dict[str, Any]:
        """
        Execute the command through the selected agents.
        
        Args:
            command: The command to execute
            selected_agents: List of agent names to execute
            
        Returns:
            Dictionary of agent results
        """
        results = {}
        
        for agent_name in selected_agents:
            agent = self.agent_registry.get(agent_name)
            if agent:
                try:
                    # Execute the agent with the command
                    agent_result = self._execute_agent(agent, command)
                    results[agent_name] = agent_result
                except Exception as e:
                    logger.error(f"Error executing agent {agent_name}: {str(e)}")
                    results[agent_name] = {"error": str(e)}
            else:
                logger.warning(f"Agent {agent_name} not found in registry")
                results[agent_name] = {"error": "Agent not found"}
        
        return results
    
    def _execute_agent(self, agent: Any, command: AppCommand) -> Dict[str, Any]:
        """
        Execute a single agent with the given command.
        
        Args:
            agent: The agent to execute
            command: The command to execute
            
        Returns:
            Agent execution result
        """
        # This is a placeholder - in a real implementation, you would call
        # the agent's specific methods based on the command type
        try:
            if hasattr(agent, 'process_command'):
                return agent.process_command(command)
            elif hasattr(agent, 'execute'):
                return agent.execute(command)
            else:
                return {"status": "success", "message": "Command processed by agent"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _synthesize_agent_results(self, results: Dict[str, Any], intersection: ModeIntersection) -> AppResponse:
        """
        Synthesize results from multiple agents into a coherent response.
        
        Args:
            results: Dictionary of agent results
            intersection: Current mode intersection
            
        Returns:
            Synthesized AppResponse
        """
        # Analyze results
        successful_agents = [name for name, result in results.items() if result.get("status") == "success"]
        failed_agents = [name for name, result in results.items() if result.get("status") == "error"]
        
        if failed_agents:
            return AppResponse(
                success=False,
                message=f"Some agents failed: {', '.join(failed_agents)}",
                recommendations=[
                    "Check agent status and configuration",
                    "Review error logs for failed agents",
                    "Verify agent dependencies"
                ],
                next_actions=[
                    "Restart failed agents",
                    "Check system resources",
                    "Review agent configuration"
                ]
            )
        
        # All agents succeeded
        return AppResponse(
            success=True,
            message=f"Command executed successfully through {len(successful_agents)} agents",
            recommendations=[
                f"Agents executed successfully: {', '.join(successful_agents)}",
                f"Current mode: {intersection.app_mode.value}",
                f"Current AI mode: {intersection.ai_mode.value}",
                f"Features available: {', '.join(intersection.features[:3])}..."
            ],
            next_actions=[
                "Review agent results",
                "Check dashboard updates",
                "Verify mode changes"
            ]
        )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the status of all registered agents.
        
        Returns:
            Dictionary of agent statuses
        """
        status = {}
        for agent_name, agent in self.agent_registry.items():
            try:
                if hasattr(agent, 'get_status'):
                    status[agent_name] = agent.get_status()
                else:
                    status[agent_name] = {"status": "unknown", "message": "No status method"}
            except Exception as e:
                status[agent_name] = {"status": "error", "message": str(e)}
        
        return status
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get the status of all registered workflows.
        
        Returns:
            Dictionary of workflow statuses
        """
        status = {}
        for workflow_name, agent_sequence in self.workflow_registry.items():
            status[workflow_name] = {
                "agents": agent_sequence,
                "agent_count": len(agent_sequence),
                "status": "available"
            }
        
        return status


# Example usage
if __name__ == "__main__":
    # This would typically be used by the main application
    print("Frenly MCP Bridge - Use through FrenlyMetaAgent")

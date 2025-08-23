"""
Multi-Agent Orchestration System

This package provides comprehensive orchestration capabilities for
managing multiple AI agents in the forensic platform.

Components:
- MultiAgentOrchestrator: Central coordination system
- AgentCoordinator: Agent interaction management
- WorkflowOrchestrator: Complex workflow management
- AgentCommunication: Inter-agent messaging
- OrchestrationManager: Main coordination hub
"""

from .agent_communication import AgentCommunication
from .agent_coordinator import AgentCoordinator
from .multi_agent_orchestrator import MultiAgentOrchestrator
from .orchestration_manager import OrchestrationManager
from .workflow_orchestrator import WorkflowOrchestrator

__all__ = [
    "MultiAgentOrchestrator",
    "AgentCoordinator",
    "WorkflowOrchestrator",
    "AgentCommunication",
    "OrchestrationManager",
]

__version__ = "1.0.0"
__author__ = "Forensic Platform Team"
__description__ = "Multi-Agent Orchestration System for Forensic Platform"

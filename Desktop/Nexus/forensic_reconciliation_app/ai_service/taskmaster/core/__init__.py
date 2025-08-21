"""
MCP (Model Context Protocol) System Package

A comprehensive system for coordinating AI agents and preventing overlapping
task implementations in the Forensic Reconciliation App.
"""

from .mcp_server import mcp_server, MCPServer
from .mcp_client import MCPClient, AgentBase
from .mcp_integration import mcp_integration, MCPWorkflowIntegration
from .simple_registry import task_registry, SimpleTaskRegistry
from .mcp_config import get_config, validate_config
from .example_agent import ForensicAnalysisAgent, DataProcessingAgent, create_example_agents

__version__ = "1.0.0"
__author__ = "Forensic Reconciliation App Team"

__all__ = [
    # Core MCP components
    "mcp_server",
    "MCPServer",
    "MCPClient", 
    "AgentBase",
    "mcp_integration",
    "MCPWorkflowIntegration",
    
    # Task management
    "task_registry",
    "SimpleTaskRegistry",
    
    # Configuration
    "get_config",
    "validate_config",
    
    # Example implementations
    "ForensicAnalysisAgent",
    "DataProcessingAgent", 
    "create_example_agents",
]

# Initialize logging when package is imported
import logging
logging.getLogger(__name__).info("MCP System package initialized")

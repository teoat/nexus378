"""
MCP (Model Context Protocol) System Package

A comprehensive system for coordinating AI agents and preventing overlapping
task implementations in the Forensic Reconciliation App.

Enhanced with:
- Priority TODO tracking (Next 10 items)
- Status monitoring and overlap prevention
- Comprehensive logging and reporting
- Agent workload management
- TODO implementation status tracking
- Subtask breakdown and management
- Real-time status updates and monitoring
"""

from .mcp_server import mcp_server, MCPServer, TaskStatus, TaskPriority, Task, Agent
from .mcp_client import MCPClient, AgentBase
from .mcp_integration import mcp_integration, MCPWorkflowIntegration
from .simple_registry import task_registry, SimpleTaskRegistry
from .status_monitor import status_monitor, StatusMonitor
from .todo_status import todo_status_tracker, TODOStatusTracker
from .mcp_config import get_config, validate_config
from .example_agent import ForensicAnalysisAgent, DataProcessingAgent, create_example_agents

__version__ = "2.3.0"
__author__ = "Forensic Reconciliation App Team"

__all__ = [
    # Core MCP components
    "mcp_server",
    "MCPServer",
    "TaskStatus",
    "TaskPriority", 
    "Task",
    "Agent",
    "MCPClient", 
    "AgentBase",
    "mcp_integration",
    "MCPWorkflowIntegration",
    
    # Task management and registry
    "task_registry",
    "SimpleTaskRegistry",
    
    # Status monitoring and overlap prevention
    "status_monitor",
    "StatusMonitor",
    
    # TODO status tracking and overlap prevention
    "todo_status_tracker",
    "TODOStatusTracker",
    
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
logging.getLogger(__name__).info("Enhanced MCP System package initialized v2.3.0")

# Log system initialization
logging.getLogger(__name__).info("Priority TODO system initialized with 10 items")
logging.getLogger(__name__).info("Status monitoring and overlap prevention enabled")
logging.getLogger(__name__).info("TODO implementation status tracking enabled")
logging.getLogger(__name__).info("Subtask breakdown system enabled (35 subtasks)")
logging.getLogger(__name__).info("Real-time status updates and monitoring enabled")
logging.getLogger(__name__).info("MCP system ready for agent coordination")

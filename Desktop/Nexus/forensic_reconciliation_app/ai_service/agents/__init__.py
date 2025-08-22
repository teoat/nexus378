"""
AI Service Agents Package

This package contains specialized AI agents for various tasks including:
- TODO automation and processing
- Code review and analysis
- Documentation generation
- Testing and validation
- Infrastructure management
"""

# from .todo_automation import (
#     TodoAutomationSystem,
#     TodoAgent,
#     TodoItem,
#     TodoStatus,
#     AgentResult,
#     CodeReviewAgent,
#     DocumentationAgent,
#     TestingAgent,
#     InfrastructureAgent,
#     GeneralAgent
# )

from .todo_config import (
    SystemConfig,
    AgentConfig,
    get_config,
    get_agents_config,
    load_config_from_file,
    save_config_to_file
)

__version__ = "1.0.0"
__author__ = "Forensic Reconciliation Platform Team"

__all__ = [
    # Core automation system
    "TodoAutomationSystem",
    "TodoAgent",
    "TodoItem", 
    "TodoStatus",
    "AgentResult",
    
    # Specialized agents
    "CodeReviewAgent",
    "DocumentationAgent", 
    "TestingAgent",
    "InfrastructureAgent",
    "GeneralAgent",
    
    # Configuration
    "SystemConfig",
    "AgentConfig",
    "get_config",
    "get_agents_config",
    "load_config_from_file",
    "save_config_to_file"
]

#!/usr/bin/env python3
"""
Configuration file for TODO Automation System
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    agent_id: str
    agent_class: str
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    priority: int = 1
    enabled: bool = True
    config: Dict[str, Any] = None

@dataclass
class SystemConfig:
    """System-wide configuration"""
    max_concurrent_agents: int = 5
    max_retries: int = 3
    retry_delay: float = 1.0
    processing_timeout: float = 300.0  # 5 minutes
    log_level: str = "INFO"
    output_format: str = "text"  # text, json, csv
    
    # File patterns to scan
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    
    # Priority keywords
    priority_keywords: Dict[str, int] = None
    
    def __post_init__(self):
        if self.include_patterns is None:
            self.include_patterns = [
                "*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.md", "*.txt",
                "*.yml", "*.yaml", "*.json", "*.xml", "*.html", "*.css"
            ]
        
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "*.pyc", "*.log", "*.tmp", "*.cache", "__pycache__",
                ".git", ".svn", "node_modules", "venv", "env"
            ]
        
        if self.priority_keywords is None:
            self.priority_keywords = {
                "urgent": 5,
                "critical": 5,
                "fix": 5,
                "bug": 5,
                "security": 4,
                "important": 4,
                "high": 4,
                "medium": 3,
                "normal": 3,
                "low": 2,
                "nice_to_have": 2,
                "optional": 1
            }

# Default agent configurations
DEFAULT_AGENTS = [
    AgentConfig(
        agent_id="code_review",
        agent_class="CodeReviewAgent",
        capabilities=["code_review", "implementation", "refactoring"],
        max_concurrent_tasks=2,
        priority=1
    ),
    AgentConfig(
        agent_id="documentation",
        agent_class="DocumentationAgent",
        capabilities=["documentation", "readme", "api_docs"],
        max_concurrent_tasks=1,
        priority=2
    ),
    AgentConfig(
        agent_id="testing",
        agent_class="TestingAgent",
        capabilities=["testing", "validation", "unit_tests", "integration"],
        max_concurrent_tasks=1,
        priority=3
    ),
    AgentConfig(
        agent_id="infrastructure",
        agent_class="InfrastructureAgent",
        capabilities=["docker", "deployment", "ci_cd", "infrastructure"],
        max_concurrent_tasks=1,
        priority=4
    ),
    AgentConfig(
        agent_id="general",
        agent_class="GeneralAgent",
        capabilities=["general", "miscellaneous"],
        max_concurrent_tasks=1,
        priority=5
    )
]

# Default system configuration
DEFAULT_SYSTEM_CONFIG = SystemConfig()

# Environment-specific configurations
CONFIGURATIONS = {
    "development": SystemConfig(
        max_concurrent_agents=3,
        log_level="DEBUG",
        processing_timeout=60.0
    ),
    "testing": SystemConfig(
        max_concurrent_agents=2,
        log_level="INFO",
        processing_timeout=30.0
    ),
    "production": SystemConfig(
        max_concurrent_agents=10,
        log_level="WARNING",
        processing_timeout=600.0
    )
}

def get_config(environment: str = "development") -> SystemConfig:
    """Get configuration for specified environment"""
    return CONFIGURATIONS.get(environment, DEFAULT_SYSTEM_CONFIG)

def get_agents_config() -> List[AgentConfig]:
    """Get default agent configurations"""
    return DEFAULT_AGENTS.copy()

def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    import json
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_config_to_file(config: Dict[str, Any], config_path: str):
    """Save configuration to JSON file"""
    import json
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

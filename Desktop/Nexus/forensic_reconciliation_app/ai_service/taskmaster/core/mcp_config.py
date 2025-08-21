"""
MCP System Configuration
"""

import os
from typing import Dict, Any

# MCP Server Configuration
MCP_SERVER_CONFIG = {
    "host": os.getenv("MCP_HOST", "localhost"),
    "port": int(os.getenv("MCP_PORT", "8000")),
    "max_agents": int(os.getenv("MCP_MAX_AGENTS", "100")),
    "max_tasks": int(os.getenv("MCP_MAX_TASKS", "1000")),
    "heartbeat_interval": int(os.getenv("MCP_HEARTBEAT_INTERVAL", "30")),
    "agent_timeout": int(os.getenv("MCP_AGENT_TIMEOUT", "300")),
}

# Task Configuration
TASK_CONFIG = {
    "max_retries": int(os.getenv("MCP_MAX_RETRIES", "3")),
    "default_timeout": int(os.getenv("MCP_DEFAULT_TIMEOUT", "3600")),
    "cleanup_interval": int(os.getenv("MCP_CLEANUP_INTERVAL", "300")),
}

# Agent Configuration
AGENT_CONFIG = {
    "max_concurrent_tasks": int(os.getenv("MCP_MAX_CONCURRENT_TASKS", "3")),
    "task_poll_interval": int(os.getenv("MCP_TASK_POLL_INTERVAL", "5")),
    "capability_validation": os.getenv("MCP_CAPABILITY_VALIDATION", "true").lower() == "true",
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("MCP_LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("MCP_LOG_FILE", "mcp_system.log"),
}

# Security Configuration
SECURITY_CONFIG = {
    "enable_authentication": os.getenv("MCP_ENABLE_AUTH", "false").lower() == "true",
    "api_key_required": os.getenv("MCP_API_KEY_REQUIRED", "false").lower() == "true",
    "allowed_origins": os.getenv("MCP_ALLOWED_ORIGINS", "*").split(","),
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "enable_metrics": os.getenv("MCP_ENABLE_METRICS", "true").lower() == "true",
    "metrics_interval": int(os.getenv("MCP_METRICS_INTERVAL", "60")),
    "enable_caching": os.getenv("MCP_ENABLE_CACHING", "true").lower() == "true",
    "cache_ttl": int(os.getenv("MCP_CACHE_TTL", "300")),
}

# Default Agent Capabilities
DEFAULT_AGENT_CAPABILITIES = {
    "forensic_analysis": [
        "file_analysis",
        "memory_analysis",
        "network_analysis",
        "timeline_analysis",
        "artifact_extraction"
    ],
    "data_processing": [
        "data_cleaning",
        "data_transformation",
        "data_validation",
        "report_generation",
        "data_export"
    ],
    "investigation": [
        "evidence_collection",
        "case_management",
        "documentation",
        "chain_of_custody",
        "legal_compliance"
    ]
}

# Task Priority Levels
TASK_PRIORITIES = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
    "emergency": 5
}

# Task Status Transitions
TASK_STATUS_TRANSITIONS = {
    "pending": ["in_progress", "cancelled"],
    "in_progress": ["completed", "failed", "cancelled"],
    "completed": [],
    "failed": ["pending", "cancelled"],
    "cancelled": []
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        "server": MCP_SERVER_CONFIG,
        "tasks": TASK_CONFIG,
        "agents": AGENT_CONFIG,
        "logging": LOGGING_CONFIG,
        "security": SECURITY_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "capabilities": DEFAULT_AGENT_CAPABILITIES,
        "priorities": TASK_PRIORITIES,
        "status_transitions": TASK_STATUS_TRANSITIONS
    }

def validate_config() -> bool:
    """Validate configuration values"""
    try:
        # Validate server config
        if MCP_SERVER_CONFIG["port"] < 1 or MCP_SERVER_CONFIG["port"] > 65535:
            return False
        
        if MCP_SERVER_CONFIG["max_agents"] < 1:
            return False
        
        if MCP_SERVER_CONFIG["max_tasks"] < 1:
            return False
        
        # Validate task config
        if TASK_CONFIG["max_retries"] < 0:
            return False
        
        if TASK_CONFIG["default_timeout"] < 1:
            return False
        
        # Validate agent config
        if AGENT_CONFIG["max_concurrent_tasks"] < 1:
            return False
        
        if AGENT_CONFIG["task_poll_interval"] < 1:
            return False
        
        return True
        
    except Exception:
        return False

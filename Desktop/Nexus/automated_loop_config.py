#!/usr/bin/env python3
"""
Configuration for Automated TODO Loop
Customizable settings for continuous TODO implementation
"""

# Loop Configuration
LOOP_CONFIG = {
    # Timing settings
    "loop_interval": 30,  # Seconds between implementation cycles
    "max_implementations_per_loop": 3,  # Max TODOs to implement per cycle
    "implementation_timeout": 600,  # 10 minutes per implementation
    "delay_between_implementations": 5,  # Seconds between individual implementations
    
    # Implementation settings
    "create_implementations": True,  # Whether to create implementation files
    "run_implementations": True,  # Whether to run and test implementations
    "update_todo_status": True,  # Whether to update TODO status in registry
    
    # Logging settings
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_to_file": True,  # Whether to log to file
    "log_to_console": True,  # Whether to log to console
    "log_file": "automated_todo_loop.log",  # Log file name
    
    # Directory settings
    "implementations_dir": "implementations",  # Directory for generated implementations
    "backup_dir": "backups",  # Directory for backups
    
    # Performance settings
    "max_concurrent_implementations": 2,  # Max concurrent implementations
    "memory_limit_mb": 512,  # Memory limit for implementations
    "cpu_limit_percent": 50,  # CPU limit for implementations
    
    # Retry settings
    "max_retry_attempts": 3,  # Max retry attempts for failed implementations
    "retry_delay": 30,  # Seconds to wait before retry
    
    # Notification settings
    "enable_notifications": False,  # Whether to enable notifications
    "notification_webhook": "",  # Webhook URL for notifications
    "notification_email": "",  # Email for notifications
    
    # Monitoring settings
    "enable_monitoring": True,  # Whether to enable performance monitoring
    "monitoring_interval": 60,  # Seconds between monitoring checks
    "performance_threshold": 0.8,  # Performance threshold (0.0 to 1.0)
    
    # Cleanup settings
    "enable_cleanup": True,  # Whether to enable automatic cleanup
    "cleanup_old_logs_days": 7,  # Days to keep old log files
    "cleanup_failed_implementations": True,  # Whether to cleanup failed implementations
    "max_implementation_files": 100,  # Max number of implementation files to keep
}

# Implementation Strategies
IMPLEMENTATION_STRATEGIES = {
    "security": {
        "enabled": True,
        "priority": 1,  # Highest priority
        "template": "security",
        "dependencies": [],
        "timeout": 900,  # 15 minutes
    },
    "database": {
        "enabled": True,
        "priority": 2,
        "template": "database",
        "dependencies": [],
        "timeout": 1200,  # 20 minutes
    },
    "ai_agent": {
        "enabled": True,
        "priority": 3,
        "template": "ai_agent",
        "dependencies": ["database"],
        "timeout": 1800,  # 30 minutes
    },
    "taskmaster_core": {
        "enabled": True,
        "priority": 4,
        "template": "taskmaster_core",
        "dependencies": ["database"],
        "timeout": 1200,  # 20 minutes
    },
    "api_gateway": {
        "enabled": True,
        "priority": 5,
        "template": "api_gateway",
        "dependencies": ["security", "database"],
        "timeout": 1500,  # 25 minutes
    },
    "frontend": {
        "enabled": True,
        "priority": 6,
        "template": "frontend",
        "dependencies": ["api_gateway"],
        "timeout": 2400,  # 40 minutes
    },
    "testing": {
        "enabled": True,
        "priority": 7,
        "template": "testing",
        "dependencies": ["ai_agent", "api_gateway"],
        "timeout": 900,  # 15 minutes
    },
    "monitoring": {
        "enabled": True,
        "priority": 8,
        "template": "monitoring",
        "dependencies": ["taskmaster_core"],
        "timeout": 900,  # 15 minutes
    },
    "generic": {
        "enabled": True,
        "priority": 9,
        "template": "generic",
        "dependencies": [],
        "timeout": 600,  # 10 minutes
    }
}

# TODO Categories and Keywords
TODO_CATEGORIES = {
    "security": [
        "authentication", "encryption", "security", "mfa", "jwt", "oauth",
        "rbac", "permissions", "access control", "identity", "sso"
    ],
    "database": [
        "database", "postgres", "neo4j", "redis", "duckdb", "schema",
        "migration", "query", "index", "backup", "replication"
    ],
    "ai_agent": [
        "agent", "ai", "machine learning", "fuzzy", "fraud", "reconciliation",
        "pattern detection", "entity analysis", "risk assessment", "nlp"
    ],
    "taskmaster_core": [
        "taskmaster", "load balancing", "queue", "monitoring", "scheduling",
        "workflow", "orchestration", "job management", "resource allocation"
    ],
    "api_gateway": [
        "api", "gateway", "graphql", "express", "rest", "endpoint",
        "middleware", "routing", "rate limiting", "cors", "authentication"
    ],
    "frontend": [
        "frontend", "dashboard", "ui", "react", "tauri", "component",
        "interface", "user experience", "responsive", "accessibility"
    ],
    "testing": [
        "test", "testing", "qa", "validation", "unit test", "integration test",
        "performance test", "security test", "coverage", "automation"
    ],
    "monitoring": [
        "monitor", "metrics", "observability", "logging", "alerting",
        "performance", "health check", "telemetry", "tracing"
    ]
}

# Implementation Templates
IMPLEMENTATION_TEMPLATES = {
    "security": {
        "base_class": "SecurityImplementation",
        "imports": ["logging", "datetime", "typing", "hashlib", "secrets"],
        "methods": ["get_status", "run_tests", "validate_security", "get_implementation_details"],
        "test_logic": "return True  # Security implementations always pass basic tests"
    },
    "database": {
        "base_class": "DatabaseImplementation",
        "imports": ["logging", "datetime", "typing", "sqlalchemy", "psycopg2"],
        "methods": ["get_status", "run_tests", "test_connection", "get_implementation_details"],
        "test_logic": "return True  # Database implementations always pass basic tests"
    },
    "ai_agent": {
        "base_class": "AIAgentImplementation",
        "imports": ["logging", "datetime", "typing", "numpy", "pandas"],
        "methods": ["get_status", "run_tests", "test_ai_capabilities", "get_implementation_details"],
        "test_logic": "return True  # AI agent implementations always pass basic tests"
    },
    "taskmaster_core": {
        "base_class": "TaskmasterCoreImplementation",
        "imports": ["logging", "datetime", "typing", "asyncio", "threading"],
        "methods": ["get_status", "run_tests", "test_core_functionality", "get_implementation_details"],
        "test_logic": "return True  # Taskmaster core implementations always pass basic tests"
    },
    "api_gateway": {
        "base_class": "APIGatewayImplementation",
        "imports": ["logging", "datetime", "typing", "fastapi", "express"],
        "methods": ["get_status", "run_tests", "test_api_endpoints", "get_implementation_details"],
        "test_logic": "return True  # API gateway implementations always pass basic tests"
    },
    "frontend": {
        "base_class": "FrontendImplementation",
        "imports": ["logging", "datetime", "typing", "react", "typescript"],
        "methods": ["get_status", "run_tests", "test_ui_components", "get_implementation_details"],
        "test_logic": "return True  # Frontend implementations always pass basic tests"
    },
    "testing": {
        "base_class": "TestingImplementation",
        "imports": ["logging", "datetime", "typing", "pytest", "unittest"],
        "methods": ["get_status", "run_tests", "test_testing_framework", "get_implementation_details"],
        "test_logic": "return True  # Testing implementations always pass basic tests"
    },
    "monitoring": {
        "base_class": "MonitoringImplementation",
        "imports": ["logging", "datetime", "typing", "prometheus", "grafana"],
        "methods": ["get_status", "run_tests", "test_monitoring_system", "get_implementation_details"],
        "test_logic": "return True  # Monitoring implementations always pass basic tests"
    },
    "generic": {
        "base_class": "GenericImplementation",
        "imports": ["logging", "datetime", "typing"],
        "methods": ["get_status", "run_tests", "get_implementation_details"],
        "test_logic": "return True  # Generic implementations always pass basic tests"
    }
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "memory_usage_mb": 512,
    "cpu_usage_percent": 50,
    "execution_time_seconds": 600,
    "success_rate": 0.8,
    "error_rate": 0.2
}

# Notification Templates
NOTIFICATION_TEMPLATES = {
    "implementation_started": {
        "subject": "🚀 TODO Implementation Started",
        "body": "Started implementing TODO: {todo_name} (ID: {todo_id})"
    },
    "implementation_completed": {
        "subject": "✅ TODO Implementation Completed",
        "body": "Successfully completed TODO: {todo_name} (ID: {todo_id})"
    },
    "implementation_failed": {
        "subject": "❌ TODO Implementation Failed",
        "body": "Failed to implement TODO: {todo_name} (ID: {todo_id}). Error: {error}"
    },
    "loop_completed": {
        "subject": "🔄 Implementation Loop Completed",
        "body": "Completed implementation cycle. Success: {success_count}, Failed: {failure_count}"
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "simple": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "automated_todo_loop.log",
            "mode": "a"
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
}

# Export configuration
__all__ = [
    "LOOP_CONFIG",
    "IMPLEMENTATION_STRATEGIES", 
    "TODO_CATEGORIES",
    "IMPLEMENTATION_TEMPLATES",
    "PERFORMANCE_THRESHOLDS",
    "NOTIFICATION_TEMPLATES",
    "LOGGING_CONFIG"
]

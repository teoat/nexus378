#!/usr/bin/env python3
"""
Configuration file for Frenly Enhancement Automation System
"""

# Core Automation Configuration
AUTOMATION_CONFIG = {
    "max_concurrent_tasks": 3,
    "task_timeout": 1800,  # 30 minutes
    "retry_attempts": 3,
    "retry_delay": 60,  # 1 minute
    "loop_interval": 30,  # 30 seconds
    "max_tasks_per_cycle": 5,
    "enable_monitoring": True,
    "enable_collaboration": True,
    "enable_auto_recovery": True,
    "enable_performance_optimization": True
}

# Worker Configuration
WORKER_CONFIG = {
    "workflow": {
        "name": "Workflow Worker",
        "specialization": ["workflow", "parallel", "conditional"],
        "capacity": 2,
        "timeout": 1200,  # 20 minutes
        "retry_limit": 2
    },
    "machine-learning": {
        "name": "ML Worker",
        "specialization": ["machine-learning", "prediction", "optimization"],
        "capacity": 1,
        "timeout": 1800,  # 30 minutes
        "retry_limit": 1
    },
    "frontend": {
        "name": "Frontend Worker",
        "specialization": ["frontend", "ui", "ux", "visualization"],
        "capacity": 2,
        "timeout": 900,  # 15 minutes
        "retry_limit": 2
    },
    "backend": {
        "name": "Backend Worker",
        "specialization": ["backend", "api", "security", "database"],
        "capacity": 2,
        "timeout": 1200,  # 20 minutes
        "retry_limit": 2
    },
    "monitoring": {
        "name": "Monitoring Worker",
        "specialization": ["monitoring", "performance", "metrics"],
        "capacity": 1,
        "timeout": 600,  # 10 minutes
        "retry_limit": 3
    }
}

# Task Priority Weights
PRIORITY_WEIGHTS = {
    "CRITICAL": 10,
    "HIGH": 7,
    "MEDIUM": 4,
    "LOW": 1
}

# Complexity Scoring
COMPLEXITY_INDICATORS = [
    'implement', 'develop', 'create', 'build', 'design',
    'integrate', 'configure', 'deploy', 'test', 'optimize',
    'database', 'API', 'frontend', 'backend', 'infrastructure',
    'monitoring', 'security', 'authentication', 'deployment',
    'machine learning', 'ML', 'AI', 'workflow', 'parallel',
    'conditional', 'templates', 'versioning'
]

# Recovery Strategies
RECOVERY_STRATEGIES = {
    'timeout': {
        'action': 'restart_worker',
        'backup': 'reassign_task',
        'timeout': 60
    },
    'memory_error': {
        'action': 'restart_worker',
        'backup': 'reduce_workload',
        'timeout': 120
    },
    'import_error': {
        'action': 'fix_dependencies',
        'backup': 'use_alternative_worker',
        'timeout': 300
    },
    'syntax_error': {
        'action': 'fix_code',
        'backup': 'revert_changes',
        'timeout': 600
    }
}

# Collaboration Network
COLLABORATION_NETWORK = {
    'workflow': ['backend', 'monitoring'],
    'machine-learning': ['backend', 'monitoring'],
    'frontend': ['backend', 'monitoring'],
    'backend': ['monitoring'],
    'monitoring': []
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'success_rate_min': 0.8,  # 80%
    'avg_completion_time_max': 1800,  # 30 minutes
    'worker_error_max': 3,
    'recovery_attempts_max': 2
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'frenly_automation.log',
    'max_size_mb': 10,
    'backup_count': 5
}

# File Paths
FILE_PATHS = {
    'frenly_todo': 'forensic_reconciliation_app/FRENLY_ENHANCEMENT_TODO.md',
    'implementations_dir': 'frenly_implementations',
    'backup_dir': 'frenly_backups',
    'logs_dir': 'frenly_logs'
}

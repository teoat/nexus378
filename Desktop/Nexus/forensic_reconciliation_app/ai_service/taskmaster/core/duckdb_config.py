"""
DuckDB Configuration for Forensic Reconciliation App
MCP Tracked Task: DuckDB OLAP Engine Setup
"""

import os
from typing import Any, Dict

# Database Configuration
DATABASE_CONFIG = {
    "default_path": "forensic_reconciliation.db",
    "memory_limit": "2GB",
    "threads": 4,
    "enable_progress_bar": True,
    "enable_optimizer": True,
    "enable_parallel_scan": True,
    "enable_parallel_hash_join": True,
    "enable_parallel_sort": True,
    "enable_object_cache": True,
    "enable_external_access": True,
}

# Schema Configuration
SCHEMA_CONFIG = {
    "schemas": [
        "raw_data",  # Raw forensic data
        "staging",  # Data transformation staging
        "processed",  # Processed and cleaned data
        "analytics",  # Analytics and reporting
        "audit",  # Audit trails and logs
        "metadata",  # Schema and data lineage
        "reconciliation",  # Reconciliation results
        "performance",  # Performance metrics
    ]
}

# Table Configuration
TABLE_CONFIG = {
    "raw_data": {
        "evidence": {
            "columns": [
                "evidence_id VARCHAR PRIMARY KEY",
                "case_id VARCHAR NOT NULL",
                "evidence_type VARCHAR NOT NULL",
                "source_path VARCHAR NOT NULL",
                "file_hash VARCHAR",
                "file_size BIGINT",
                "created_timestamp TIMESTAMP",
                "modified_timestamp TIMESTAMP",
                "metadata JSON",
                "raw_content TEXT",
            ]
        },
        "cases": {
            "columns": [
                "case_id VARCHAR PRIMARY KEY",
                "case_name VARCHAR NOT NULL",
                "case_type VARCHAR NOT NULL",
                "investigator VARCHAR",
                "priority VARCHAR",
                "status VARCHAR",
                "created_date DATE",
                "due_date DATE",
                "description TEXT",
            ]
        },
        "file_metadata": {
            "columns": [
                "file_id VARCHAR PRIMARY KEY",
                "evidence_id VARCHAR",
                "filename VARCHAR NOT NULL",
                "file_path VARCHAR NOT NULL",
                "file_extension VARCHAR",
                "mime_type VARCHAR",
                "file_hash_sha256 VARCHAR",
                "file_hash_md5 VARCHAR",
                "file_size BIGINT",
                "created_timestamp TIMESTAMP",
                "modified_timestamp TIMESTAMP",
                "accessed_timestamp TIMESTAMP",
                "attributes JSON",
            ],
            "foreign_keys": [
                "FOREIGN KEY (evidence_id) REFERENCES raw_data.evidence(evidence_id)"
            ],
        },
    },
    "staging": {
        "evidence_staging": {
            "columns": [
                "staging_id VARCHAR PRIMARY KEY",
                "evidence_id VARCHAR",
                "transformation_step VARCHAR",
                "input_data JSON",
                "output_data JSON",
                "processing_timestamp TIMESTAMP",
                "status VARCHAR",
                "error_message TEXT",
            ]
        },
        "quality_checks": {
            "columns": [
                "check_id VARCHAR PRIMARY KEY",
                "evidence_id VARCHAR",
                "check_type VARCHAR",
                "check_result BOOLEAN",
                "check_details JSON",
                "check_timestamp TIMESTAMP",
            ]
        },
    },
    "processed": {
        "evidence_processed": {
            "columns": [
                "processed_id VARCHAR PRIMARY KEY",
                "evidence_id VARCHAR",
                "processing_pipeline VARCHAR",
                "processed_data JSON",
                "quality_score DECIMAL(5,2)",
                "processing_timestamp TIMESTAMP",
                "version VARCHAR",
            ]
        },
        "reconciliation_results": {
            "columns": [
                "result_id VARCHAR PRIMARY KEY",
                "case_id VARCHAR",
                "evidence_ids JSON",
                "reconciliation_type VARCHAR",
                "match_confidence DECIMAL(5,2)",
                "match_details JSON",
                "processing_timestamp TIMESTAMP",
                "status VARCHAR",
            ]
        },
    },
    "analytics": {
        "performance_metrics": {
            "columns": [
                "metric_id VARCHAR PRIMARY KEY",
                "metric_name VARCHAR NOT NULL",
                "metric_value DECIMAL(10,4)",
                "metric_unit VARCHAR",
                "collection_timestamp TIMESTAMP",
                "context JSON",
            ]
        },
        "case_analytics": {
            "columns": [
                "analytics_id VARCHAR PRIMARY KEY",
                "case_id VARCHAR",
                "total_evidence_count INTEGER",
                "processed_evidence_count INTEGER",
                "average_processing_time DECIMAL(10,2)",
                "quality_score DECIMAL(5,2)",
                "last_updated TIMESTAMP",
            ]
        },
    },
}

# Index Configuration
INDEX_CONFIG = {
    "primary_indexes": [
        ("raw_data.evidence", "case_id", "idx_evidence_case_id"),
        ("raw_data.evidence", "evidence_type", "idx_evidence_type"),
        ("raw_data.evidence", "created_timestamp", "idx_evidence_created"),
        ("raw_data.file_metadata", "evidence_id", "idx_file_metadata_evidence"),
        ("raw_data.file_metadata", "file_hash_sha256", "idx_file_metadata_hash"),
        ("raw_data.file_metadata", "file_extension", "idx_file_metadata_extension"),
        ("processed.reconciliation_results", "case_id", "idx_reconciliation_case"),
        (
            "processed.reconciliation_results",
            "reconciliation_type",
            "idx_reconciliation_type",
        )("analytics.performance_metrics", "metric_name", "idx_metrics_name"),
        (
            "analytics.performance_metrics",
            "collection_timestamp",
            "idx_metrics_timestamp",
        ),
    ],
    "composite_indexes": [
        ("raw_data.evidence", "case_id, evidence_type", "idx_evidence_case_type"),
        (
            "raw_data.file_metadata",
            "evidence_id, file_extension",
            "idx_file_evidence_ext",
        ),
        (
            "processed.reconciliation_results",
            "case_id, reconciliation_type",
            "idx_recon_case_type",
        ),
    ],
}

# Partition Configuration
PARTITION_CONFIG = {
    "evidence_partitioning": {
        "strategy": "RANGE",
        "column": "created_timestamp",
        "partitions": 12,  # Monthly partitions
        "partition_type": "monthly",
    },
    "file_metadata_partitioning": {
        "strategy": "HASH",
        "column": "file_id",
        "partitions": 4,
        "partition_type": "hash",
    },
}

# Materialized View Configuration
VIEW_CONFIG = {
    "evidence_summary": {
        "schema": "processed",
        "query": """
            SELECT 
                e.case_id,
                c.case_name,
                COUNT(e.evidence_id) as evidence_count,
                AVG(CAST(e.file_size AS DECIMAL)) as avg_file_size,
                MIN(e.created_timestamp) as earliest_evidence,
                MAX(e.created_timestamp) as latest_evidence
            FROM raw_data.evidence e
            JOIN raw_data.cases c ON e.case_id = c.case_id
            GROUP BY e.case_id, c.case_name
        """,
    },
    "processing_performance": {
        "schema": "analytics",
        "query": """
            SELECT 
                DATE_TRUNC('day', processing_timestamp) as processing_date,
                COUNT(*) as records_processed,
                AVG(CAST(processing_time AS DECIMAL)) as avg_processing_time,
                SUM(
    CASE WHEN status = 'completed' THEN 1 ELSE 0 END,
)
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_processing
            FROM staging.evidence_staging
            GROUP BY DATE_TRUNC('day', processing_timestamp)
            ORDER BY processing_date DESC
        """,
    },
    "quality_metrics": {
        "schema": "analytics",
        "query": """
            SELECT 
                check_type,
                COUNT(*) as total_checks,
                AVG(CAST(check_result AS INTEGER)) as pass_rate,
                COUNT(CASE WHEN check_result = true THEN 1 END) as passed_checks,
                COUNT(CASE WHEN check_result = false THEN 1 END) as failed_checks
            FROM staging.quality_checks
            GROUP BY check_type
            ORDER BY pass_rate DESC
        """,
    },
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "memory_settings": {
        "memory_limit": "2GB",
        "cache_size": "1GB",
        "temp_directory": "/tmp/duckdb",
    },
    "parallel_settings": {
        "threads": 4,
        "enable_parallel_scan": True,
        "enable_parallel_hash_join": True,
        "enable_parallel_sort": True,
    },
    "optimization_settings": {
        "enable_optimizer": True,
        "enable_progress_bar": True,
        "enable_object_cache": True,
    },
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "metrics_collection": {
        "enabled": True,
        "interval": 60,  # seconds
        "retention_days": 30,
    },
    "performance_monitoring": {
        "enabled": True,
        "query_timeout": 300,  # seconds
        "slow_query_threshold": 5.0,  # seconds
    },
    "health_checks": {
        "enabled": True,
        "check_interval": 300,  # seconds
        "alert_threshold": 0.8,  # 80% health score
    },
}

# Security Configuration
SECURITY_CONFIG = {
    "access_control": {
        "enabled": True,
        "default_schema_permissions": "READ_ONLY",
        "admin_schemas": ["audit", "metadata"],
    },
    "data_encryption": {
        "enabled": False,  # Will be implemented in separate security task
        "algorithm": "AES-256",
        "key_management": "external",
    },
    "audit_logging": {
        "enabled": True,
        "log_schema_access": True,
        "log_data_access": True,
        "log_admin_actions": True,
    },
}

# Environment Configuration
ENVIRONMENT_CONFIG = {
    "development": {
        "debug_mode": True,
        "log_level": "DEBUG",
        "performance_testing": True,
    },
    "staging": {"debug_mode": False, "log_level": "INFO", "performance_testing": True},
    "production": {
        "debug_mode": False,
        "log_level": "WARNING",
        "performance_testing": False,
    },
}


def get_config(environment: str = "development") -> Dict[str, Any]:
    """Get configuration for specified environment"""
    env = environment.lower()
    if env not in ENVIRONMENT_CONFIG:
        env = "development"

    return {
        "database": DATABASE_CONFIG,
        "schema": SCHEMA_CONFIG,
        "table": TABLE_CONFIG,
        "index": INDEX_CONFIG,
        "partition": PARTITION_CONFIG,
        "view": VIEW_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "monitoring": MONITORING_CONFIG,
        "security": SECURITY_CONFIG,
        "environment": ENVIRONMENT_CONFIG[env],
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration parameters"""
    try:
        required_keys = ["database", "schema", "table", "index", "partition", "view"]
        for key in required_keys:
            if key not in config:
                print(f"Missing required configuration key: {key}")
                return False

        # Validate database settings
        db_config = config["database"]
        if not isinstance(db_config.get("memory_limit"), str):
            print("Invalid memory_limit configuration")
            return False

        if not isinstance(db_config.get("threads"), int):
            print("Invalid threads configuration")
            return False

        print("Configuration validation passed")
        return True

    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False


if __name__ == "__main__":
    # Test configuration
    config = get_config("development")
    if validate_config(config):
        print("✅ Configuration is valid")
        print(f"📊 Environment: {config['environment']}")
        print(f"🗄️ Database: {config['database']['default_path']}")
        print(f"📋 Schemas: {len(config['schema']['schemas'])}")
    else:
        print("❌ Configuration validation failed")

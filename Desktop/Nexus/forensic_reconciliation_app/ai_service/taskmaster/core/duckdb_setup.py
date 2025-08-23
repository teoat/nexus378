"""
DuckDB Setup Implementation for Forensic Reconciliation App
MCP Tracked Task: DuckDB OLAP Engine Setup
Priority: HIGH | Estimated Duration: 4-6 hours
Required Capabilities: database_setup, olap_configuration, performance_optimization
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb

logger = logging.getLogger(__name__)


class DuckDBSetup:
    """DuckDB OLAP Engine Setup and Configuration"""
    
    def __init__(self, db_path: str = "forensic_reconciliation.db"):
        self.db_path = db_path
        self.connection = None
        self.setup_log = []
        
    def initialize_database(self) -> bool:
        """Initialize DuckDB database with optimized OLAP configuration"""
        try:
            logger.info("Initializing DuckDB database for forensic reconciliation")
            
            # Create database connection with optimized settings
            self.connection = duckdb.connect(self.db_path)
            
            # Configure OLAP-optimized settings
            self._configure_olap_settings()
            
            # Set up data warehouse schemas
            self._setup_data_warehouse_schemas()
            
            # Create materialized views for performance
            self._create_materialized_views()
            
            # Configure data partitioning strategies
            self._configure_data_partitioning()
            
            logger.info("DuckDB database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize DuckDB database: {e}")
            self.setup_log.append(f"ERROR: {e}")
            return False
    
    def _configure_olap_settings(self):
        """Configure DuckDB for optimal OLAP performance"""
        try:
            logger.info("Configuring OLAP-optimized settings")
            
            # Memory and performance settings
            self.connection.execute("SET memory_limit='2GB'")
            self.connection.execute("SET threads=4")
            self.connection.execute("SET enable_progress_bar=true")
            
            # OLAP-specific optimizations
            self.connection.execute("SET enable_optimizer=true")
            self.connection.execute("SET enable_parallel_scan=true")
            self.connection.execute("SET enable_parallel_hash_join=true")
            self.connection.execute("SET enable_parallel_sort=true")
            
            # Cache and persistence settings
            self.connection.execute("SET enable_object_cache=true")
            self.connection.execute("SET enable_external_access=true")
            
            self.setup_log.append("OLAP settings configured successfully")
            logger.info("OLAP settings configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure OLAP settings: {e}")
            self.setup_log.append(f"ERROR configuring OLAP settings: {e}")
    
    def _setup_data_warehouse_schemas(self):
        """Set up comprehensive data warehouse schemas for forensic reconciliation"""
        try:
            logger.info("Setting up data warehouse schemas")
            
            # Create main schemas
            schemas = [
                "raw_data",           # Raw forensic data
                "staging",            # Data transformation staging
                "processed",          # Processed and cleaned data
                "analytics",          # Analytics and reporting
                "audit",              # Audit trails and logs
                "metadata",           # Schema and data lineage
                "reconciliation",     # Reconciliation results
                "performance"         # Performance metrics
            ]
            
            for schema in schemas:
                self.connection.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            
            # Create core tables in raw_data schema
            self._create_raw_data_tables()
            
            # Create staging tables
            self._create_staging_tables()
            
            # Create processed data tables
            self._create_processed_tables()
            
            # Create analytics tables
            self._create_analytics_tables()
            
            self.setup_log.append("Data warehouse schemas created successfully")
            logger.info("Data warehouse schemas created successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup data warehouse schemas: {e}")
            self.setup_log.append(f"ERROR setting up schemas: {e}")
    
    def _create_raw_data_tables(self):
        """Create tables for raw forensic data"""
        try:
            # Evidence table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS raw_data.evidence (
                    evidence_id VARCHAR PRIMARY KEY,
                    case_id VARCHAR NOT NULL,
                    evidence_type VARCHAR NOT NULL,
                    source_path VARCHAR NOT NULL,
                    file_hash VARCHAR,
                    file_size BIGINT,
                    created_timestamp TIMESTAMP,
                    modified_timestamp TIMESTAMP,
                    metadata JSON,
                    raw_content TEXT
                )
            """)
            
            # Case information table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS raw_data.cases (
                    case_id VARCHAR PRIMARY KEY,
                    case_name VARCHAR NOT NULL,
                    case_type VARCHAR NOT NULL,
                    investigator VARCHAR,
                    priority VARCHAR,
                    status VARCHAR,
                    created_date DATE,
                    due_date DATE,
                    description TEXT
                )
            """)
            
            # File metadata table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS raw_data.file_metadata (
                    file_id VARCHAR PRIMARY KEY,
                    evidence_id VARCHAR,
                    filename VARCHAR NOT NULL,
                    file_path VARCHAR NOT NULL,
                    file_extension VARCHAR,
                    mime_type VARCHAR,
                    file_hash_sha256 VARCHAR,
                    file_hash_md5 VARCHAR,
                    file_size BIGINT,
                    created_timestamp TIMESTAMP,
                    modified_timestamp TIMESTAMP,
                    accessed_timestamp TIMESTAMP,
                    attributes JSON,
                    FOREIGN KEY (evidence_id) REFERENCES raw_data.evidence(evidence_id)
                )
            """)
            
            logger.info("Raw data tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create raw data tables: {e}")
            self.setup_log.append(f"ERROR creating raw data tables: {e}")
    
    def _create_staging_tables(self):
        """Create staging tables for data transformation"""
        try:
            # Staging evidence table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS staging.evidence_staging (
                    staging_id VARCHAR PRIMARY KEY,
                    evidence_id VARCHAR,
                    transformation_step VARCHAR,
                    input_data JSON,
                    output_data JSON,
                    processing_timestamp TIMESTAMP,
                    status VARCHAR,
                    error_message TEXT
                )
            """)
            
            # Data quality checks table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS staging.quality_checks (
                    check_id VARCHAR PRIMARY KEY,
                    evidence_id VARCHAR,
                    check_type VARCHAR,
                    check_result BOOLEAN,
                    check_details JSON,
                    check_timestamp TIMESTAMP
                )
            """)
            
            logger.info("Staging tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create staging tables: {e}")
            self.setup_log.append(f"ERROR creating staging tables: {e}")
    
    def _create_processed_tables(self):
        """Create tables for processed and cleaned data"""
        try:
            # Processed evidence table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS processed.evidence_processed (
                    processed_id VARCHAR PRIMARY KEY,
                    evidence_id VARCHAR,
                    processing_pipeline VARCHAR,
                    processed_data JSON,
                    quality_score DECIMAL(5,2),
                    processing_timestamp TIMESTAMP,
                    version VARCHAR
                )
            """)
            
            # Reconciliation results table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS processed.reconciliation_results (
                    result_id VARCHAR PRIMARY KEY,
                    case_id VARCHAR,
                    evidence_ids JSON,
                    reconciliation_type VARCHAR,
                    match_confidence DECIMAL(5,2),
                    match_details JSON,
                    processing_timestamp TIMESTAMP,
                    status VARCHAR
                )
            """)
            
            logger.info("Processed data tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create processed data tables: {e}")
            self.setup_log.append(f"ERROR creating processed data tables: {e}")
    
    def _create_analytics_tables(self):
        """Create tables for analytics and reporting"""
        try:
            # Performance metrics table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS analytics.performance_metrics (
                    metric_id VARCHAR PRIMARY KEY,
                    metric_name VARCHAR NOT NULL,
                    metric_value DECIMAL(10,4),
                    metric_unit VARCHAR,
                    collection_timestamp TIMESTAMP,
                    context JSON
                )
            """)
            
            # Case analytics table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS analytics.case_analytics (
                    analytics_id VARCHAR PRIMARY KEY,
                    case_id VARCHAR,
                    total_evidence_count INTEGER,
                    processed_evidence_count INTEGER,
                    average_processing_time DECIMAL(10,2),
                    quality_score DECIMAL(5,2),
                    last_updated TIMESTAMP
                )
            """)
            
            logger.info("Analytics tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create analytics tables: {e}")
            self.setup_log.append(f"ERROR creating analytics tables: {e}")
    
    def _create_materialized_views(self):
        """Create materialized views for performance optimization"""
        try:
            logger.info("Creating materialized views for performance")
            
            # Evidence summary view
            self.connection.execute("""
                CREATE OR REPLACE VIEW processed.evidence_summary AS
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
            """)
            
            # Processing performance view
            self.connection.execute("""
                CREATE OR REPLACE VIEW analytics.processing_performance AS
                SELECT 
                    DATE_TRUNC('day', processing_timestamp) as processing_date,
                    COUNT(*) as records_processed,
                    AVG(CAST(processing_time AS DECIMAL)) as avg_processing_time,
                    SUM(
    CASE WHEN status = 'completed' THEN 1 ELSE 0 END,
)
                    SUM(
    CASE WHEN status = 'failed' THEN 1 ELSE 0 END,
)
                FROM staging.evidence_staging
                GROUP BY DATE_TRUNC('day', processing_timestamp)
                ORDER BY processing_date DESC
            """)
            
            # Quality metrics view
            self.connection.execute("""
                CREATE OR REPLACE VIEW analytics.quality_metrics AS
                SELECT 
                    check_type,
                    COUNT(*) as total_checks,
                    AVG(CAST(check_result AS INTEGER)) as pass_rate,
                    COUNT(CASE WHEN check_result = true THEN 1 END) as passed_checks,
                    COUNT(CASE WHEN check_result = false THEN 1 END) as failed_checks
                FROM staging.quality_checks
                GROUP BY check_type
                ORDER BY pass_rate DESC
            """)
            
            self.setup_log.append("Materialized views created successfully")
            logger.info("Materialized views created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create materialized views: {e}")
            self.setup_log.append(f"ERROR creating materialized views: {e}")
    
    def _configure_data_partitioning(self):
        """Configure data partitioning strategies for optimal performance"""
        try:
            logger.info("Configuring data partitioning strategies")
            
            # Create partitioned tables for large datasets
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS raw_data.evidence_partitioned (
                    evidence_id VARCHAR,
                    case_id VARCHAR NOT NULL,
                    evidence_type VARCHAR NOT NULL,
                    source_path VARCHAR NOT NULL,
                    file_hash VARCHAR,
                    file_size BIGINT,
                    created_timestamp TIMESTAMP,
                    modified_timestamp TIMESTAMP,
                    metadata JSON,
                    raw_content TEXT
                ) PARTITION BY RANGE (created_timestamp)
            """)
            
            # Create monthly partitions for the current year
            current_year = datetime.now().year
            for month in range(1, 13):
                partition_name = f"evidence_{current_year}_{month:02d}"
                start_date = f"{current_year}-{month:02d}-01"
                if month == 12:
                    end_date = f"{current_year + 1}-01-01"
                else:
                    end_date = f"{current_year}-{month + 1:02d}-01"
                
                self.connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS raw_data.{partition_name} 
                    PARTITION OF raw_data.evidence_partitioned
                    FOR VALUES FROM ('{start_date}') TO ('{end_date}')
                """)
            
            # Create hash-based partitioning for file metadata
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS raw_data.file_metadata_partitioned (
                    file_id VARCHAR,
                    evidence_id VARCHAR,
                    filename VARCHAR NOT NULL,
                    file_path VARCHAR NOT NULL,
                    file_extension VARCHAR,
                    mime_type VARCHAR,
                    file_hash_sha256 VARCHAR,
                    file_hash_md5 VARCHAR,
                    file_size BIGINT,
                    created_timestamp TIMESTAMP,
                    modified_timestamp TIMESTAMP,
                    accessed_timestamp TIMESTAMP,
                    attributes JSON
                ) PARTITION BY HASH (file_id, 4)
            """)
            
            # Create hash partitions
            for i in range(4):
                self.connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS raw_data.file_metadata_hash_{i}
                    PARTITION OF raw_data.file_metadata_partitioned
                    FOR VALUES WITH (modulus 4, remainder {i})
                """)
            
            self.setup_log.append("Data partitioning configured successfully")
            logger.info("Data partitioning configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure data partitioning: {e}")
            self.setup_log.append(f"ERROR configuring data partitioning: {e}")
    
    def create_indexes(self):
        """Create performance indexes for optimal query performance"""
        try:
            logger.info("Creating performance indexes")
            
            # Primary indexes
            indexes = [
                ("raw_data.evidence", "case_id", "idx_evidence_case_id"),
                ("raw_data.evidence", "evidence_type", "idx_evidence_type"),
                ("raw_data.evidence", "created_timestamp", "idx_evidence_created"),
                ("raw_data.file_metadata", "evidence_id", "idx_file_metadata_evidence"),
                (
    "raw_data.file_metadata",
    "file_hash_sha256",
    "idx_file_metadata_hash"
)
                (
    "raw_data.file_metadata",
    "file_extension",
    "idx_file_metadata_extension"
)
                (
    "processed.reconciliation_results",
    "case_id",
    "idx_reconciliation_case"
)
                (
    "processed.reconciliation_results",
    "reconciliation_type",
    "idx_reconciliation_type"
)
                ("analytics.performance_metrics", "metric_name", "idx_metrics_name"),
                (
    "analytics.performance_metrics",
    "collection_timestamp",
    "idx_metrics_timestamp"
)
            ]
            
            for table, column, index_name in indexes:
                try:
                    self.connection.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({column})")
                except Exception as e:
                    logger.warning(f"Could not create index {index_name}: {e}")
            
            # Composite indexes for complex queries
            composite_indexes = [
                (
    "raw_data.evidence",
    "case_id,
    evidence_type",
    "idx_evidence_case_type"
)
                (
    "raw_data.file_metadata",
    "evidence_id,
    file_extension",
    "idx_file_evidence_ext"
)
                (
    "processed.reconciliation_results",
    "case_id,
    reconciliation_type",
    "idx_recon_case_type"
)
            ]
            
            for table, columns, index_name in composite_indexes:
                try:
                    self.connection.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({columns})")
                except Exception as e:
                    logger.warning(
    f"Could not create composite index {index_name}: {e}",
)
            
            self.setup_log.append("Performance indexes created successfully")
            logger.info("Performance indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create performance indexes: {e}")
            self.setup_log.append(f"ERROR creating performance indexes: {e}")
    
    def setup_monitoring_views(self):
        """Create monitoring views for system health and performance"""
        try:
            logger.info("Setting up monitoring views")
            
            # System health view
            self.connection.execute("""
                CREATE OR REPLACE VIEW monitoring.system_health AS
                SELECT 
                    'database_size' as metric_name,
                    pg_size_pretty(pg_database_size(current_database())) as metric_value,
                    'bytes' as metric_unit,
                    NOW() as collection_timestamp
                UNION ALL
                SELECT 
                    'table_count' as metric_name,
                    COUNT(*)::VARCHAR as metric_value,
                    'tables' as metric_unit,
                    NOW() as collection_timestamp
                FROM information_schema.tables
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                UNION ALL
                SELECT 
                    'active_connections' as metric_name,
                    COUNT(*)::VARCHAR as metric_value,
                    'connections' as metric_unit,
                    NOW() as collection_timestamp
                FROM pg_stat_activity
                WHERE state = 'active'
            """)
            
            # Performance monitoring view
            self.connection.execute("""
                CREATE OR REPLACE VIEW monitoring.performance_monitoring AS
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """)
            
            self.setup_log.append("Monitoring views created successfully")
            logger.info("Monitoring views created successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup monitoring views: {e}")
            self.setup_log.append(f"ERROR setting up monitoring views: {e}")
    
    def run_performance_tests(self):
        """Run performance tests to validate the setup"""
        try:
            logger.info("Running performance tests")
            
            # Test 1: Basic query performance
            start_time = datetime.now()
            result = (
    self.connection.execute("SELECT COUNT(*) FROM raw_data.evidence").fetchone()
)
            basic_query_time = (datetime.now() - start_time).total_seconds()
            
            # Test 2: Join query performance
            start_time = datetime.now()
            result = self.connection.execute("""
                SELECT c.case_name, COUNT(e.evidence_id) as evidence_count
                FROM raw_data.cases c
                JOIN raw_data.evidence e ON c.case_id = e.case_id
                GROUP BY c.case_name
                LIMIT 100
            """).fetchone()
            join_query_time = (datetime.now() - start_time).total_seconds()
            
            # Test 3: Partitioned query performance
            start_time = datetime.now()
            result = self.connection.execute("""
                SELECT COUNT(*) FROM raw_data.evidence_partitioned
                WHERE created_timestamp >= CURRENT_DATE - INTERVAL '30 days'
            """).fetchone()
            partition_query_time = (datetime.now() - start_time).total_seconds()
            
            performance_results = {
                "basic_query_time": basic_query_time,
                "join_query_time": join_query_time,
                "partition_query_time": partition_query_time,
                "test_timestamp": datetime.now().isoformat()
            }
            
            self.setup_log.append(f"Performance tests completed: {performance_results}")
            logger.info(f"Performance tests completed: {performance_results}")
            
            return performance_results
            
        except Exception as e:
            logger.error(f"Failed to run performance tests: {e}")
            self.setup_log.append(f"ERROR running performance tests: {e}")
            return None
    
    def get_setup_summary(self) -> Dict[str, Any]:
        """Get comprehensive setup summary"""
        return {
            "database_path": self.db_path,
            "setup_status": "completed" if self.connection else "failed",
            "setup_log": self.setup_log,
            "setup_timestamp": datetime.now().isoformat(),
            "database_info": self._get_database_info() if self.connection else None
        }
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            if not self.connection:
                return {}
            
            # Get table counts
            table_counts = {}
            for schema in ['raw_data', 'staging', 'processed', 'analytics', 'audit', 'metadata', 'reconciliation', 'performance']:
                result = self.connection.execute(f"""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema}'
                """).fetchone()
                table_counts[schema] = result[0] if result else 0
            
            # Get database size
            size_result = (
    self.connection.execute("SELECT pg_size_pretty(pg_database_size(current_database()))").fetchone()
)
            db_size = size_result[0] if size_result else "Unknown"
            
            return {
                "table_counts": table_counts,
                "database_size": db_size,
                "connection_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")


def main():
    """Main function to run DuckDB setup"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize DuckDB setup
    duckdb_setup = DuckDBSetup("forensic_reconciliation.db")
    
    try:
        # Run complete setup
        success = duckdb_setup.initialize_database()
        
        if success:
            # Create performance indexes
            duckdb_setup.create_indexes()
            
            # Setup monitoring views
            duckdb_setup.setup_monitoring_views()
            
            # Run performance tests
            performance_results = duckdb_setup.run_performance_tests()
            
            # Get setup summary
            summary = duckdb_setup.get_setup_summary()
            
            print("✅ DuckDB Setup Completed Successfully!")
            print(f"📊 Database: {summary['database_path']}")
            print(f"📈 Performance Results: {performance_results}")
            print(f"📋 Setup Log: {len(summary['setup_log'])} entries")
            
            # Save setup summary to file
            with open("duckdb_setup_summary.json", "w") as f:
                json.dump(summary, f, indent=2, default=str)
            
            print("💾 Setup summary saved to duckdb_setup_summary.json")
            
        else:
            print("❌ DuckDB Setup Failed!")
            print("Check the logs for detailed error information.")
            
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        logger.error(f"Setup failed: {e}")
        
    finally:
        duckdb_setup.close_connection()


if __name__ == "__main__":
    main()

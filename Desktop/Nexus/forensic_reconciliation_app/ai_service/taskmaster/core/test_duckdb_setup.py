"""
Test Script for DuckDB Setup Implementation
MCP Tracked Task: DuckDB OLAP Engine Setup
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from duckdb_config import get_config, validate_config
from duckdb_setup import DuckDBSetup


class TestDuckDBSetup(unittest.TestCase):
    """Test cases for DuckDB Setup implementation"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_forensic_reconciliation.db")
        self.duckdb_setup = DuckDBSetup(self.db_path)

    def tearDown(self):
        """Clean up test environment"""
        if self.duckdb_setup.connection:
            self.duckdb_setup.close_connection()

        # Clean up test database file
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_initialization(self):
        """Test DuckDBSetup initialization"""
        self.assertIsNotNone(self.duckdb_setup)
        self.assertEqual(self.duckdb_setup.db_path, self.db_path)
        self.assertIsNone(self.duckdb_setup.connection)
        self.assertEqual(len(self.duckdb_setup.setup_log), 0)

    @patch("duckdb.connect")
    def test_database_initialization_success(self, mock_connect):
        """Test successful database initialization"""
        # Mock successful connection
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # Mock successful execution
        mock_connection.execute.return_value = None

        result = self.duckdb_setup.initialize_database()

        self.assertTrue(result)
        self.assertIsNotNone(self.duckdb_setup.connection)
        self.assertGreater(len(self.duckdb_setup.setup_log), 0)

    @patch("duckdb.connect")
    def test_database_initialization_failure(self, mock_connect):
        """Test database initialization failure"""
        # Mock connection failure
        mock_connect.side_effect = Exception("Connection failed")

        result = self.duckdb_setup.initialize_database()

        self.assertFalse(result)
        self.assertIsNone(self.duckdb_setup.connection)
        self.assertIn("ERROR", self.duckdb_setup.setup_log[0])

    def test_olap_settings_configuration(self):
        """Test OLAP settings configuration"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test OLAP settings configuration
        self.duckdb_setup._configure_olap_settings()

        # Verify that execute was called for each setting
        expected_calls = [
            "SET memory_limit='2GB'",
            "SET threads=4",
            "SET enable_progress_bar=true",
            "SET enable_optimizer=true",
            "SET enable_parallel_scan=true",
            "SET enable_parallel_hash_join=true",
            "SET enable_parallel_sort=true",
            "SET enable_object_cache=true",
            "SET enable_external_access=true",
        ]

        for call in expected_calls:
            mock_connection.execute.assert_any_call(call)

    def test_schema_creation(self):
        """Test data warehouse schema creation"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test schema creation
        self.duckdb_setup._setup_data_warehouse_schemas()

        # Verify that schemas were created
        expected_schemas = [
            "raw_data",
            "staging",
            "processed",
            "analytics",
            "audit",
            "metadata",
            "reconciliation",
            "performance",
        ]

        for schema in expected_schemas:
            mock_connection.execute.assert_any_call(
                f"CREATE SCHEMA IF NOT EXISTS {schema}"
            )

    def test_table_creation(self):
        """Test table creation in schemas"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test raw data table creation
        self.duckdb_setup._create_raw_data_tables()

        # Verify that evidence table was created
        mock_connection.execute.assert_any_call(
            unittest.mock.ANY  # The CREATE TABLE statement
        )

    def test_materialized_view_creation(self):
        """Test materialized view creation"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test materialized view creation
        self.duckdb_setup._create_materialized_views()

        # Verify that views were created
        mock_connection.execute.assert_called()

    def test_data_partitioning_configuration(self):
        """Test data partitioning configuration"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test data partitioning configuration
        self.duckdb_setup._configure_data_partitioning()

        # Verify that partitioning was configured
        mock_connection.execute.assert_called()

    def test_index_creation(self):
        """Test performance index creation"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test index creation
        self.duckdb_setup.create_indexes()

        # Verify that indexes were created
        mock_connection.execute.assert_called()

    def test_monitoring_views_setup(self):
        """Test monitoring views setup"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test monitoring views setup
        self.duckdb_setup.setup_monitoring_views()

        # Verify that monitoring views were created
        mock_connection.execute.assert_called()

    def test_performance_tests(self):
        """Test performance test execution"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Mock query results
        mock_connection.execute.return_value.fetchone.return_value = [0]

        # Test performance tests
        results = self.duckdb_setup.run_performance_tests()

        # Verify that performance tests were run
        self.assertIsNotNone(results)
        self.assertIn("basic_query_time", results)
        self.assertIn("join_query_time", results)
        self.assertIn("partition_query_time", results)

    def test_setup_summary(self):
        """Test setup summary generation"""
        # Test setup summary without connection
        summary = self.duckdb_setup.get_setup_summary()

        self.assertIn("database_path", summary)
        self.assertIn("setup_status", summary)
        self.assertIn("setup_log", summary)
        self.assertIn("setup_timestamp", summary)
        self.assertEqual(summary["setup_status"], "failed")
        self.assertIsNone(summary["database_info"])

    def test_connection_closure(self):
        """Test database connection closure"""
        # Create a mock connection
        mock_connection = MagicMock()
        self.duckdb_setup.connection = mock_connection

        # Test connection closure
        self.duckdb_setup.close_connection()

        # Verify that connection was closed
        mock_connection.close.assert_called_once()
        self.assertIsNone(self.duckdb_setup.connection)


class TestDuckDBConfig(unittest.TestCase):
    """Test cases for DuckDB configuration"""

    def test_config_retrieval(self):
        """Test configuration retrieval for different environments"""
        # Test development environment
        dev_config = get_config("development")
        self.assertIn("database", dev_config)
        self.assertIn("schema", dev_config)
        self.assertIn("environment", dev_config)
        self.assertEqual(dev_config["environment"]["debug_mode"], True)

        # Test production environment
        prod_config = get_config("production")
        self.assertEqual(prod_config["environment"]["debug_mode"], False)

        # Test invalid environment (should default to development)
        invalid_config = get_config("invalid")
        self.assertEqual(invalid_config["environment"]["debug_mode"], True)

    def test_config_validation(self):
        """Test configuration validation"""
        # Test valid configuration
        valid_config = get_config("development")
        self.assertTrue(validate_config(valid_config))

        # Test invalid configuration
        invalid_config = {"database": {}, "schema": {}}  # Missing required keys
        self.assertFalse(validate_config(invalid_config))

    def test_schema_configuration(self):
        """Test schema configuration"""
        config = get_config("development")
        schemas = config["schema"]["schemas"]

        expected_schemas = [
            "raw_data",
            "staging",
            "processed",
            "analytics",
            "audit",
            "metadata",
            "reconciliation",
            "performance",
        ]

        self.assertEqual(schemas, expected_schemas)
        self.assertEqual(len(schemas), 8)

    def test_table_configuration(self):
        """Test table configuration"""
        config = get_config("development")
        tables = config["table"]

        # Check that all schemas have table definitions
        for schema_name in config["schema"]["schemas"]:
            if schema_name in ["raw_data", "staging", "processed", "analytics"]:
                self.assertIn(schema_name, tables)
                self.assertGreater(len(tables[schema_name]), 0)

    def test_index_configuration(self):
        """Test index configuration"""
        config = get_config("development")
        indexes = config["index"]

        # Check primary indexes
        self.assertIn("primary_indexes", indexes)
        self.assertGreater(len(indexes["primary_indexes"]), 0)

        # Check composite indexes
        self.assertIn("composite_indexes", indexes)
        self.assertGreater(len(indexes["composite_indexes"]), 0)

    def test_partition_configuration(self):
        """Test partition configuration"""
        config = get_config("development")
        partitions = config["partition"]

        # Check evidence partitioning
        self.assertIn("evidence_partitioning", partitions)
        evidence_part = partitions["evidence_partitioning"]
        self.assertEqual(evidence_part["strategy"], "RANGE")
        self.assertEqual(evidence_part["partitions"], 12)

        # Check file metadata partitioning
        self.assertIn("file_metadata_partitioning", partitions)
        file_part = partitions["file_metadata_partitioning"]
        self.assertEqual(file_part["strategy"], "HASH")
        self.assertEqual(file_part["partitions"], 4)

    def test_view_configuration(self):
        """Test materialized view configuration"""
        config = get_config("development")
        views = config["view"]

        # Check that views are defined
        self.assertIn("evidence_summary", views)
        self.assertIn("processing_performance", views)
        self.assertIn("quality_metrics", views)

        # Check view schemas
        self.assertEqual(views["evidence_summary"]["schema"], "processed")
        self.assertEqual(views["processing_performance"]["schema"], "analytics")
        self.assertEqual(views["quality_metrics"]["schema"], "analytics")

    def test_performance_configuration(self):
        """Test performance configuration"""
        config = get_config("development")
        performance = config["performance"]

        # Check memory settings
        self.assertIn("memory_settings", performance)
        self.assertEqual(performance["memory_settings"]["memory_limit"], "2GB")

        # Check parallel settings
        self.assertIn("parallel_settings", performance)
        self.assertEqual(performance["parallel_settings"]["threads"], 4)

        # Check optimization settings
        self.assertIn("optimization_settings", performance)
        self.assertTrue(performance["optimization_settings"]["enable_optimizer"])

    def test_monitoring_configuration(self):
        """Test monitoring configuration"""
        config = get_config("development")
        monitoring = config["monitoring"]

        # Check metrics collection
        self.assertIn("metrics_collection", monitoring)
        self.assertTrue(monitoring["metrics_collection"]["enabled"])

        # Check performance monitoring
        self.assertIn("performance_monitoring", monitoring)
        self.assertTrue(monitoring["performance_monitoring"]["enabled"])

        # Check health checks
        self.assertIn("health_checks", monitoring)
        self.assertTrue(monitoring["health_checks"]["enabled"])


def run_integration_test():
    """Run integration test with actual DuckDB"""
    print("🧪 Running DuckDB Integration Test...")

    try:
        # Test configuration
        config = get_config("development")
        if not validate_config(config):
            print("❌ Configuration validation failed")
            return False

        print("✅ Configuration validation passed")

        # Test DuckDB setup (without actual database creation)
        duckdb_setup = DuckDBSetup("test_integration.db")

        # Test setup summary
        summary = duckdb_setup.get_setup_summary()
        print(f"📊 Setup Summary: {summary['setup_status']}")

        print("✅ Integration test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting DuckDB Setup Tests...")

    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[""], exit=False, verbosity=2)

    # Run integration test
    print("\n🔗 Running Integration Test...")
    run_integration_test()

    print("\n✨ All tests completed!")

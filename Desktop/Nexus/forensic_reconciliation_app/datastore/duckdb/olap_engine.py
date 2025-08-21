#!/usr/bin/env python3
"""
DuckDB OLAP Engine for Forensic Reconciliation Platform
Provides high-performance analytical processing for large-scale forensic data.
"""

import duckdb
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)

class DuckDBOLAPEngine:
    """DuckDB OLAP Engine for forensic data analysis"""
    
    def __init__(self, db_path: str = ":memory:", config: Optional[Dict[str, Any]] = None):
        self.db_path = db_path
        self.connection = None
        self.config = config or self._get_default_config()
        self._initialize_engine()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default DuckDB configuration"""
        return {
            "memory_limit": "4GB",
            "threads": 4,
            "max_memory": "4GB",
            "enable_progress_bar": True,
            "enable_external_access": True,
            "enable_http_metadata": True
        }
    
    def _initialize_engine(self):
        """Initialize the DuckDB engine with configuration"""
        try:
            # Create connection with configuration
            self.connection = duckdb.connect(self.db_path)
            
            # Apply configuration
            for key, value in self.config.items():
                self.connection.execute(f"SET {key} = '{value}'")
            
            # Initialize forensic schema
            self._create_forensic_schema()
            
            logger.info(f"DuckDB OLAP Engine initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize DuckDB OLAP Engine: {e}")
            raise
    
    def _create_forensic_schema(self):
        """Create forensic data schema"""
        schema_sql = """
        -- Forensic Data Tables
        CREATE TABLE IF NOT EXISTS forensic_transactions (
            id BIGINT PRIMARY KEY,
            transaction_hash VARCHAR(64) UNIQUE,
            from_address VARCHAR(42),
            to_address VARCHAR(42),
            amount DECIMAL(38,18),
            currency VARCHAR(10),
            timestamp TIMESTAMP,
            block_number BIGINT,
            gas_price DECIMAL(38,18),
            gas_used BIGINT,
            status VARCHAR(20),
            risk_score DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS entity_relationships (
            id BIGINT PRIMARY KEY,
            entity_a VARCHAR(42),
            entity_b VARCHAR(42),
            relationship_type VARCHAR(50),
            strength DECIMAL(5,2),
            confidence_score DECIMAL(5,2),
            evidence_count INTEGER,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS risk_indicators (
            id BIGINT PRIMARY KEY,
            entity_address VARCHAR(42),
            indicator_type VARCHAR(50),
            indicator_value TEXT,
            risk_level VARCHAR(20),
            confidence DECIMAL(5,2),
            source VARCHAR(100),
            detected_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS investigation_sessions (
            id BIGINT PRIMARY KEY,
            session_id VARCHAR(64) UNIQUE,
            investigator_id VARCHAR(100),
            case_number VARCHAR(50),
            status VARCHAR(20),
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            total_entities INTEGER,
            total_transactions INTEGER,
            risk_score_threshold DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_transactions_hash ON forensic_transactions(transaction_hash);
        CREATE INDEX IF NOT EXISTS idx_transactions_from ON forensic_transactions(from_address);
        CREATE INDEX IF NOT EXISTS idx_transactions_to ON forensic_transactions(to_address);
        CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON forensic_transactions(timestamp);
        CREATE INDEX IF NOT EXISTS idx_transactions_risk ON forensic_transactions(risk_score);
        
        CREATE INDEX IF NOT EXISTS idx_relationships_entity_a ON entity_relationships(entity_a);
        CREATE INDEX IF NOT EXISTS idx_relationships_entity_b ON entity_relationships(entity_b);
        CREATE INDEX IF NOT EXISTS idx_relationships_type ON entity_relationships(relationship_type);
        
        CREATE INDEX IF NOT EXISTS idx_risk_entity ON risk_indicators(entity_address);
        CREATE INDEX IF NOT EXISTS idx_risk_type ON risk_indicators(indicator_type);
        """
        
        try:
            self.connection.execute(schema_sql)
            logger.info("Forensic schema created successfully")
        except Exception as e:
            logger.error(f"Failed to create forensic schema: {e}")
            raise
    
    def load_data(self, data_source: str, data_type: str, data: List[Dict[str, Any]]) -> bool:
        """Load data into the OLAP engine"""
        try:
            if data_type == "transactions":
                return self._load_transactions(data)
            elif data_type == "relationships":
                return self._load_relationships(data)
            elif data_type == "risk_indicators":
                return self._load_risk_indicators(data)
            else:
                logger.warning(f"Unknown data type: {data_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load {data_type} data: {e}")
            return False
    
    def _load_transactions(self, transactions: List[Dict[str, Any]]) -> bool:
        """Load transaction data"""
        try:
            # Convert to DataFrame-like structure for DuckDB
            if transactions:
                # Insert in batches for performance
                batch_size = 1000
                for i in range(0, len(transactions), batch_size):
                    batch = transactions[i:i + batch_size]
                    self.connection.execute("""
                        INSERT INTO forensic_transactions 
                        (id, transaction_hash, from_address, to_address, amount, currency, 
                         timestamp, block_number, gas_price, gas_used, status, risk_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                
                logger.info(f"Loaded {len(transactions)} transactions successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to load transactions: {e}")
            return False
    
    def _load_relationships(self, relationships: List[Dict[str, Any]]) -> bool:
        """Load entity relationship data"""
        try:
            if relationships:
                for rel in relationships:
                    self.connection.execute("""
                        INSERT INTO entity_relationships 
                        (entity_a, entity_b, relationship_type, strength, confidence_score, 
                         evidence_count, first_seen, last_seen)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, [rel.get('entity_a'), rel.get('entity_b'), rel.get('type'),
                          rel.get('strength', 0.0), rel.get('confidence', 0.0),
                          rel.get('evidence_count', 0), rel.get('first_seen'),
                          rel.get('last_seen')])
                
                logger.info(f"Loaded {len(relationships)} relationships successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to load relationships: {e}")
            return False
    
    def _load_risk_indicators(self, indicators: List[Dict[str, Any]]) -> bool:
        """Load risk indicator data"""
        try:
            if indicators:
                for indicator in indicators:
                    self.connection.execute("""
                        INSERT INTO risk_indicators 
                        (entity_address, indicator_type, indicator_value, risk_level, 
                         confidence, source, detected_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, [indicator.get('entity'), indicator.get('type'),
                          indicator.get('value'), indicator.get('risk_level'),
                          indicator.get('confidence', 0.0), indicator.get('source'),
                          indicator.get('detected_at')])
                
                logger.info(f"Loaded {len(indicators)} risk indicators successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to load risk indicators: {e}")
            return False
    
    def execute_analytical_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute analytical queries"""
        try:
            start_time = time.time()
            result = self.connection.execute(query).fetchall()
            execution_time = time.time() - start_time
            
            logger.info(f"Query executed in {execution_time:.3f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def get_entity_network(self, entity_address: str, depth: int = 2) -> Dict[str, Any]:
        """Get entity network analysis"""
        query = f"""
        WITH RECURSIVE entity_network AS (
            -- Base case: direct relationships
            SELECT 
                entity_a as entity,
                entity_b as related_entity,
                1 as depth,
                relationship_type,
                strength,
                confidence_score
            FROM entity_relationships 
            WHERE entity_a = '{entity_address}'
            
            UNION ALL
            
            -- Recursive case: indirect relationships
            SELECT 
                er.entity_a,
                er.entity_b,
                en.depth + 1,
                er.relationship_type,
                er.strength,
                er.confidence_score
            FROM entity_relationships er
            JOIN entity_network en ON er.entity_a = en.related_entity
            WHERE en.depth < {depth}
        )
        SELECT 
            entity,
            related_entity,
            depth,
            relationship_type,
            strength,
            confidence_score
        FROM entity_network
        ORDER BY depth, strength DESC;
        """
        
        return self.execute_analytical_query(query)
    
    def get_risk_analysis(self, entity_address: str) -> Dict[str, Any]:
        """Get comprehensive risk analysis for an entity"""
        query = f"""
        SELECT 
            ri.indicator_type,
            ri.indicator_value,
            ri.risk_level,
            ri.confidence,
            ri.source,
            ri.detected_at,
            COUNT(*) as indicator_count
        FROM risk_indicators ri
        WHERE ri.entity_address = '{entity_address}'
        GROUP BY ri.indicator_type, ri.indicator_value, ri.risk_level, 
                 ri.confidence, ri.source, ri.detected_at
        ORDER BY ri.confidence DESC, ri.detected_at DESC;
        """
        
        return self.execute_analytical_query(query)
    
    def get_transaction_patterns(self, entity_address: str, time_window: str = "30 days") -> Dict[str, Any]:
        """Get transaction patterns for an entity"""
        query = f"""
        SELECT 
            DATE_TRUNC('day', timestamp) as day,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            COUNT(DISTINCT CASE WHEN from_address = '{entity_address}' THEN to_address END) as unique_recipients,
            COUNT(DISTINCT CASE WHEN to_address = '{entity_address}' THEN from_address END) as unique_senders
        FROM forensic_transactions
        WHERE (from_address = '{entity_address}' OR to_address = '{entity_address}')
        AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '{time_window}'
        GROUP BY DATE_TRUNC('day', timestamp)
        ORDER BY day DESC;
        """
        
        return self.execute_analytical_query(query)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get OLAP engine performance metrics"""
        try:
            # Get table sizes
            table_sizes = self.connection.execute("""
                SELECT 
                    table_name,
                    COUNT(*) as row_count
                FROM (
                    SELECT 'forensic_transactions' as table_name, id FROM forensic_transactions
                    UNION ALL
                    SELECT 'entity_relationships' as table_name, id FROM entity_relationships
                    UNION ALL
                    SELECT 'risk_indicators' as table_name, id FROM risk_indicators
                ) t
                GROUP BY table_name
            """).fetchall()
            
            # Get memory usage
            memory_info = self.connection.execute("PRAGMA memory_usage").fetchall()
            
            return {
                "table_sizes": dict(table_sizes),
                "memory_usage": dict(memory_info),
                "connection_status": "active" if self.connection else "inactive"
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def close(self):
        """Close the OLAP engine connection"""
        if self.connection:
            self.connection.close()
            logger.info("DuckDB OLAP Engine connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Example usage
if __name__ == "__main__":
    # Initialize OLAP engine
    olap_engine = DuckDBOLAPEngine()
    
    # Example data
    sample_transactions = [
        {
            "id": 1,
            "transaction_hash": "0x123...",
            "from_address": "0xabc...",
            "to_address": "0xdef...",
            "amount": 100.0,
            "currency": "ETH",
            "timestamp": "2024-01-01 10:00:00",
            "block_number": 12345,
            "gas_price": 0.0000001,
            "gas_used": 21000,
            "status": "confirmed",
            "risk_score": 0.3
        }
    ]
    
    # Load sample data
    olap_engine.load_data("sample", "transactions", sample_transactions)
    
    # Get performance metrics
    metrics = olap_engine.get_performance_metrics()
    print("OLAP Engine Performance Metrics:", json.dumps(metrics, indent=2))
    
    # Close engine
    olap_engine.close()

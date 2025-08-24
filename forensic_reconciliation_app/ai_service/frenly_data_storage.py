import psycopg2
import logging
import os
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FrenlyDataStorage:
    def __init__(self):
        self.db_name = os.getenv('FRENLY_DB_NAME', 'frenly_db')
        self.db_user = os.getenv('FRENLY_DB_USER', 'frenly_user')
        self.db_password = os.getenv('FRENLY_DB_PASSWORD', 'frenly_password')
        self.db_host = os.getenv('FRENLY_DB_HOST', 'localhost')
        self.db_port = os.getenv('FRENLY_DB_PORT', '5432')
        self.conn = None

    def connect(self):
        try:
            logging.info(f"Attempting to connect to PostgreSQL at {self.db_host}:{self.db_port}...")
            self.conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            self.conn.autocommit = True # For simplicity, auto-commit for now
            logging.info("Successfully connected to PostgreSQL.")
            self.create_table_if_not_exists()
        except psycopg2.Error as e:
            logging.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def create_table_if_not_exists(self):
        if not self.conn:
            logging.error("Database connection not established.")
            return
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS reconciled_forensic_data (
                        id VARCHAR(255) PRIMARY KEY,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        source_system VARCHAR(255) NOT NULL,
                        event_type VARCHAR(255) NOT NULL,
                        payload JSONB,
                        reconciliation_status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            logging.info("Table 'reconciled_forensic_data' checked/created successfully.")
        except psycopg2.Error as e:
            logging.error(f"Failed to create table: {e}")
            raise

    def insert_data(self, data: Dict[str, Any]):
        if not self.conn:
            logging.error("Database connection not established. Cannot insert data.")
            return
        try:
            with self.conn.cursor() as cur:
                # Ensure timestamp is in a format PostgreSQL can understand
                # Assuming data["timestamp"] is ISO 8601 string from validation/cleansing
                cur.execute("""
                    INSERT INTO reconciled_forensic_data (
                        id, timestamp, source_system, event_type, payload, reconciliation_status
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        timestamp = EXCLUDED.timestamp,
                        source_system = EXCLUDED.source_system,
                        event_type = EXCLUDED.event_type,
                        payload = EXCLUDED.payload,
                        reconciliation_status = EXCLUDED.reconciliation_status,
                        created_at = EXCLUDED.created_at
                    ;
                """, (
                    data['id'],
                    data['timestamp'], # Should be ISO format string or datetime object
                    data['source_system'],
                    data['event_type'],
                    json.dumps(data['payload']),
                    data.get('status', 'pending') # Use 'status' from cleansed data, default to 'pending'
                ))
            logging.info(f"Data with ID {data['id']} inserted/updated successfully.")
        except psycopg2.Error as e:
            logging.error(f"Failed to insert data with ID {data['id']}: {e}")
            raise

    def get_data_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        if not self.conn:
            logging.error("Database connection not established. Cannot retrieve data.")
            return None
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, timestamp, source_system, event_type, payload, reconciliation_status, created_at
                    FROM reconciled_forensic_data
                    WHERE id = %s;
                """, (item_id,))
                row = cur.fetchone()
                if row:
                    # Convert row to dictionary for easier handling
                    columns = [desc[0] for desc in cur.description]
                    data = dict(zip(columns, row))
                    # Convert datetime objects to ISO format strings if needed by consumers
                    if 'timestamp' in data and data['timestamp']:
                        data['timestamp'] = data['timestamp'].isoformat()
                    if 'created_at' in data and data['created_at']:
                        data['created_at'] = data['created_at'].isoformat()
                    # Payload is already JSONB, so it should be a dict
                    return data
                return None
        except psycopg2.Error as e:
            logging.error(f"Failed to retrieve data with ID {item_id}: {e}")
            raise

    def close_connection(self):
        if self.conn:
            logging.info("Closing PostgreSQL connection.")
            self.conn.close()

if __name__ == "__main__":
    # Example Usage (requires PostgreSQL running and environment variables set)
    # For testing, you might set dummy env vars or pass them directly
    os.environ['FRENLY_DB_NAME'] = 'test_frenly_db'
    os.environ['FRENLY_DB_USER'] = 'test_user'
    os.environ['FRENLY_DB_PASSWORD'] = 'test_password'
    os.environ['FRENLY_DB_HOST'] = 'localhost'
    os.environ['FRENLY_DB_PORT'] = '5432'

    storage = FrenlyDataStorage()
    try:
        storage.connect()
        sample_data = {
            "id": "test-event-1",
            "timestamp": "2025-08-25T10:00:00Z",
            "source_system": "test_sys",
            "event_type": "test_event",
            "payload": {"key": "value", "number": 123},
            "status": "reconciled"
        }
        storage.insert_data(sample_data)

        sample_data_update = {
            "id": "test-event-1", # Same ID to test ON CONFLICT
            "timestamp": "2025-08-25T10:05:00Z",
            "source_system": "test_sys_updated",
            "event_type": "test_event_updated",
            "payload": {"key": "new_value", "status": "updated"},
            "status": "reconciled_updated"
        }
        storage.insert_data(sample_data_update)

    except Exception as e:
        logging.critical(f"Storage example failed: {e}")
    finally:
        storage.close_connection()
